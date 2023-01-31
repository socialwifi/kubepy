import collections
import copy
import logging
import time

from kubepy import api
from kubepy import definition_manager
from kubepy import definition_transformers

logger = logging.getLogger(__name__)


class InstallError(Exception):
    pass


class JobError(InstallError):
    pass


class PodError(JobError):
    def __init__(self, message='', container_name='', stdout='', stderr=''):
        self.container_name = container_name
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(message, container_name, stdout, stderr)


class DeadlineExceeded(JobError):
    pass


def directory_applier(path, options):
    manager = definition_manager.DefinitionManager(path)
    return DefinitionsApplier(manager, options)


DirectoryApplier = directory_applier


def directories_applier(paths, options):
    manager = definition_manager.OverridenDefinitionManager(
        *(definition_manager.DefinitionManager(path) for path in paths),
    )
    return DefinitionsApplier(manager, options)


DirectoriesApplier = directories_applier


class DefinitionsApplier:
    def __init__(self, manager, options):
        self.options = options
        self.manager = manager

    def apply_all(self):
        for definition in self.manager.values():
            UniversalDefinitionApplier(definition, self.options).apply()

    def apply_named(self, name):
        definition = self.manager[name]
        UniversalDefinitionApplier(definition, self.options).apply()

    def get_named_definition(self, name):
        definition = self.manager[name]
        return UniversalDefinitionApplier(definition, self.options).new_definition


class BaseDefinitionApplier:
    def __init__(self, definition, options, namespace=None):
        self.definition = definition
        self.options = options
        self.namespace = namespace

    def apply(self):
        raise NotImplementedError

    @property
    def usable_with(self):
        raise NotImplementedError

    @property
    def new_definition(self):
        raise NotImplementedError


class ResourceApplier(BaseDefinitionApplier):
    custom_resource_definitions = ['ServiceMonitor', 'PodMonitor', 'PrometheusRule', 'AlertmanagerConfig']
    usable_with = ['Service', 'Secret', 'ConfigMap', 'StorageClass', 'PersistentVolume',
                   'PersistentVolumeClaim', 'Ingress', 'PodDisruptionBudget',
                   *custom_resource_definitions]

    def apply(self):
        try:
            api.apply(self.definition, namespace=self.namespace)
        except api.ApiError as e:
            for crd in self.custom_resource_definitions:
                if 'no matches for kind "{}"'.format(crd) in str(e):
                    logger.warning('Custom Resource named "{}" not found! '
                                   'Please install it first, skipping for now.'.format(crd))
                    break
            else:
                raise


class ReplicatedTemplateResourceApplier(BaseDefinitionApplier):
    usable_with = ['Deployment', 'StatefulSet']

    def apply(self):
        if self.options.replace:
            api.replace(self.new_definition, namespace=self.namespace)
        else:
            api.apply(self.new_definition, namespace=self.namespace)

    @property
    def new_definition(self):
        return transform_pod_definition(self.definition, self.options)


class CronJobApplier(BaseDefinitionApplier):
    usable_with = ['CronJob']

    def apply(self):
        api.apply(self.new_definition, namespace=self.namespace)

    @property
    def new_definition(self):
        return transform_pod_definition(self.definition, self.options)


class BaseJobApplier(BaseDefinitionApplier):
    def apply(self):
        api.create(self.new_definition, namespace=self.namespace)
        try:
            while True:
                status = self._get_status()
                status.raise_if_failed()
                if status.succeeded:
                    break
                else:
                    time.sleep(1)
        finally:
            api.delete(self.definition_type, self.name, namespace=self.namespace)

    def _get_status(self):
        return self.status_class(self.name, self._get_raw_status())

    def _get_raw_status(self):
        return api.get(self.definition_type, self.name, namespace=self.namespace)['status']

    @property
    def new_definition(self):
        return transform_pod_definition(self.definition, self.options)

    @property
    def name(self):
        return self.definition['metadata']['name']

    @property
    def status_class(self):
        raise NotImplementedError

    @property
    def definition_type(self):
        raise NotImplementedError


class BaseJobStatus:
    def __init__(self, definition_name, status, namespace=None):
        self.definition_name = definition_name
        self.status = status
        self.namespace = namespace

    def raise_if_failed(self):
        raise NotImplementedError

    def succeeded(self):
        raise NotImplementedError


class JobStatus(BaseJobStatus):
    def __init__(self, definition_name, status, max_retires=0, namespace=None):
        super().__init__(definition_name, status, namespace)
        self.max_retries = max_retires

    def raise_if_failed(self):
        if 'conditions' in self.status:
            condition = self.status['conditions'][0]
            if condition['type'] == 'Failed':
                self._raise_for_failed_condition(condition)
        failures = self.status.get('failed', 0)
        if failures > self.max_retries:
            failed_pod = self.get_job_pod()
            if failed_pod:
                stdout = self.get_failed_pod_logs(failed_pod)
                print(stdout)
            raise JobError('Job failed {} times.'.format(failures))

    def get_failed_pod_logs(self, failed_pod):
        for init_container_status in failed_pod['status'].get('initContainerStatuses', []):
            if init_container_status['state'].get('terminated', {}).get('reason') == 'ContainerCannotRun':
                return 'Init container failed! ' + str(init_container_status['state']['terminated']['message'])
        for container_status in failed_pod['status'].get('containerStatuses', []):
            if container_status['state'].get('terminated', {}).get('reason') == 'ContainerCannotRun':
                return 'Container failed! ' + str(container_status['state']['terminated']['message'])
        name = failed_pod['metadata']['name']
        namespace = failed_pod['metadata'].get('namespace')
        return api.logs(name, namespace=namespace)[0].decode()

    def _raise_for_failed_condition(self, condition):
        if condition['reason'] == 'DeadlineExceeded':
            raise DeadlineExceeded(condition['message'])
        else:
            raise JobError(condition['message'])

    @property
    def succeeded(self):
        return 'completionTime' in self.status

    def get_job_pod(self):
        pods = api.get_failed_pod_for_job(self.definition_name, namespace=self.namespace)['items']
        if not pods:
            logging.warning('No pod found for job {}!'.format(self.definition_name))
            return
        elif len(pods) > 1:
            logging.info('More than one pod found for job {}, returning first.'.format(self.definition_name))
        return pods[0]


ContainerInfo = collections.namedtuple('ContainerInfo', ['name', 'state'])


class PodStatus(BaseJobStatus):
    def raise_if_failed(self):
        for container in self.containers:
            if 'terminated' in container.state:
                if container.state['terminated']['reason'] != 'Completed':
                    self.raise_with_log(container.name)

    @property
    def succeeded(self):
        for container in self.containers:
            terminated = 'terminated' in container.state
            completed = terminated and container.state['terminated']['reason'] == 'Completed'
            if not completed:
                return False
        else:
            return True

    @property
    def containers(self):
        for container_status in self.status['containerStatuses']:
            yield ContainerInfo(container_status['name'], container_status['state'])

    def raise_with_log(self, container_name):
        stdout, stderr = api.logs(self.definition_name, container_name)
        raise PodError('Failure in {}'.format(container_name), container_name, stdout, stderr)


class JobApplier(BaseJobApplier):
    definition_type = 'Job'
    usable_with = [definition_type]
    status_class = JobStatus

    def _get_status(self):
        return self.status_class(self.name, self._get_raw_status(), self.options.max_job_retries,
                                 namespace=self.namespace)


class PodApplier(BaseJobApplier):
    definition_type = 'Pod'
    usable_with = [definition_type]
    status_class = PodStatus

    def apply(self):
        if self.definition['spec']['restartPolicy'] != 'Never':
            raise JobError('Pod has to have restartPolicy = Never')
        super().apply()


class UniversalDefinitionApplier(BaseDefinitionApplier):
    applier_classes = (ResourceApplier, ReplicatedTemplateResourceApplier, CronJobApplier, JobApplier, PodApplier)
    usable_with = sum((applier.usable_with for applier in applier_classes), [])

    def apply(self):
        self.get_applier().apply()

    @property
    def kind_map(self):
        kind_map = UniqueDict()
        for applier_class in self.applier_classes:
            for kind in applier_class.usable_with:
                kind_map[kind] = applier_class
        return dict(kind_map)

    @property
    def new_definition(self):
        return self.get_applier().new_definition

    def get_applier(self):
        kind = self.definition['kind']
        namespace = self.definition['metadata'].get('namespace')
        try:
            applier_class = self.kind_map[kind]
        except KeyError:
            raise InstallError('Unknown resource kind: {}'.format(kind))
        else:
            return applier_class(self.definition, self.options, namespace=namespace)


class UniqueDictException(Exception):
    pass


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)
        else:
            raise UniqueDictException(key)


def transform_pod_definition(definition, options):
    new_definition = copy.deepcopy(definition)
    new_definition = definition_transformers.tag_untaged_images(new_definition, options.build_tag)
    new_definition = definition_transformers.set_environment(new_definition, options.environment)
    new_definition = definition_transformers.add_host_volumes(new_definition, options.host_volumes)
    new_definition = definition_transformers.add_labels(new_definition, options.labels, options.pod_labels)
    new_definition = definition_transformers.add_annotations(
        new_definition, options.annotations, options.pod_annotations)
    return new_definition
