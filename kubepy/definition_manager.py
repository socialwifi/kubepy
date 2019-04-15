import collections
import contextlib
import itertools
import pathlib

import yaml

from kubepy import definition_merger


class BaseDefinitionManager(collections.Mapping):
    def __len__(self):
        return len(list(self))

    def __or__(self, other):
        return OverridenDefinitionManager(self, other)


class OverridenDefinitionManager(BaseDefinitionManager):
    def __init__(self, *managers):
        self.managers = managers

    def __getitem__(self, name):
        definitions = list(self.get_inner_definitions(name))
        if not definitions:
            raise KeyError
        else:
            return definition_merger.merge_definitions(*definitions)

    def get_inner_definitions(self, name):
        for manager in self.managers:
            with contextlib.suppress(KeyError):
                yield manager[name]

    def __iter__(self):
        yield from sorted(set(itertools.chain(*(manager.keys() for manager in self.managers))))


class DefinitionManager(BaseDefinitionManager):
    def __init__(self, directory: pathlib.Path):
        self.directory = directory

    def __getitem__(self, name):
        path = self.get_path_from_name(name)
        if path.exists():
            return self.get_yaml_from_file(path)
        else:
            raise KeyError('{} does not exist'.format(path))

    def __iter__(self):
        for path in sorted(self.directory.glob('*.yml')):
            yield path.name[:-4]

    def __len__(self):
        return len(list(self))

    def get_path_from_name(self, name):
        return self.directory / (name + '.yml')

    def get_yaml_from_file(self, path):
        with path.open() as yaml_file:
            return yaml.safe_load(yaml_file)
