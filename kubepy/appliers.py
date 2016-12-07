import copy

import time

from kubepy import api
from kubepy import definition_manager
from kubepy import definition_transformers


class InstallError(Exception):
    pass


class JobError(InstallError):
    pass


class DeadlineExceeded(JobError):
    pass


class DirectoryApplier:
    def __init__(self, path, options):
        self.options = options
        self.manager = definition_manager.DefinitionManager(path)

    def apply_all(self):
        for definition in self.manager.get_sorted_definitions():
            UniversalDefinitionApplier(definition, self.options).apply()

    def apply_named(self, name):
        definition = self.manager.get_definition(name)
        UniversalDefinitionApplier(definition, self.options).apply()


class BaseDefinitionApplier:
    def __init__(self, definition, options):
        self.definition = definition
        self.options = options

    def apply(self):
        raise NotImplementedError

    @property
    def usable_with(self):
        raise NotImplementedError


class ResourceApplier(BaseDefinitionApplier):
    usable_with = ['Service', 'Secret']

    def apply(self):
        api.apply(self.definition)


class DeploymentApplier(BaseDefinitionApplier):
    usable_with = ['Deployment']

    def apply(self):
        if self.options.replace:
            api.replace(self.new_definition)
        else:
            api.apply(self.new_definition)

    @property
    def new_definition(self):
        return transform_container_definition(self.definition, self.options)


class BaseJobApplier(BaseDefinitionApplier):
    def apply(self):
        api.create(self.new_definition)
        try:
            while True:
                status = self._get_status()
                status.raise_if_failed()
                if status.succeeded:
                    break
                else:
                    time.sleep(1)
        finally:
            api.delete(self.definition_type, self.name)

    def _get_status(self):
        return self.status_class(api.get(self.definition_type, [('app', self.app)])['items'][0]['status'])

    @property
    def new_definition(self):
        return transform_container_definition(self.definition, self.options)

    @property
    def name(self):
        return self.definition['metadata']['name']

    @property
    def app(self):
        return self.definition['metadata']['labels']['app']

    @property
    def status_class(self):
        raise NotImplementedError

    @property
    def definition_type(self):
        raise NotImplementedError


class BaseJobStatus:
    def __init__(self, status):
        self.status = status

    def raise_if_failed(self):
        raise NotImplementedError

    def succeeded(self):
        raise NotImplementedError


class JobStatus(BaseJobStatus):
    def raise_if_failed(self):
        if 'conditions' in self.status:
            condition = self.status['conditions'][0]
            if condition['type'] == 'Failed':
                self._raise_for_failed_condition(condition)

    def _raise_for_failed_condition(self, condition):
        if condition['reason'] == 'DeadlineExceeded':
            raise DeadlineExceeded(condition['message'])
        else:
            raise JobError(condition['message'])

    @property
    def succeeded(self):
        return 'completionTime' in self.status


class PodStatus(BaseJobStatus):
    def raise_if_failed(self):
        for state in self.container_states:
            if 'terminated' in state:
                if state['terminated']['reason'] != 'Completed':
                    raise JobError(state['terminated']['reason'])

    @property
    def succeeded(self):
        for state in self.container_states:
            terminated = 'terminated' in state
            completed = terminated and state['terminated']['reason'] == 'Completed'
            if not completed:
                return False
        else:
            return True

    @property
    def container_states(self):
        for container_status in self.status['containerStatuses']:
            yield container_status['state']


class JobApplier(BaseJobApplier):
    definition_type = 'Job'
    usable_with = [definition_type]
    status_class = JobStatus


class PodApplier(BaseJobApplier):
    definition_type = 'Pod'
    usable_with = [definition_type]
    status_class = PodStatus

    def apply(self):
        if self.definition['spec']['restartPolicy'] != 'Never':
            raise JobError('Pod has to have restartPolicy = Never')
        super().apply()


class UniversalDefinitionApplier(BaseDefinitionApplier):
    applier_classes = (ResourceApplier, DeploymentApplier, JobApplier, PodApplier)
    usable_with = sum((applier.usable_with for applier in applier_classes), [])

    def apply(self):
        kind = self.definition['kind']
        try:
            applier_class = self.kind_map[kind]
        except KeyError:
            raise InstallError('Unknown resource kind: {}'.format(kind))
        else:
            applier = applier_class(self.definition, self.options)
            applier.apply()

    @property
    def kind_map(self):
        kind_map = UniqueDict()
        for applier_class in self.applier_classes:
            for kind in applier_class.usable_with:
                kind_map[kind] = applier_class
        return dict(kind_map)


class UniqueDictException(Exception):
    pass


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)
        else:
            raise UniqueDictException(key)


def transform_container_definition(definition, options):
    new_definition = copy.deepcopy(definition)
    new_definition = definition_transformers.tag_untaged_images(new_definition, options.build_tag)
    return new_definition
