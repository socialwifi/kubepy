import copy

import time

from kubepy import api
from kubepy import definition_manager
from kubepy import definition_transformers


class InstallError(Exception):
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


class JobApplier(BaseDefinitionApplier):
    usable_with = ['Job']

    def apply(self):
        api.create(self.new_definition)
        try:
            while True:
                status = api.get('job', [('app', self.app)])['items'][0]['status']
                if 'completionTime' in status:
                    break
                else:
                    time.sleep(1)
        finally:
            api.delete('job', self.name)

    @property
    def new_definition(self):
        return transform_container_definition(self.definition, self.options)

    @property
    def name(self):
        return self.definition['metadata']['name']

    @property
    def app(self):
        return self.definition['metadata']['labels']['app']


class UniversalDefinitionApplier(BaseDefinitionApplier):
    applier_classes = (ResourceApplier, DeploymentApplier, JobApplier)
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
