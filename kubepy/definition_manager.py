import collections
import pathlib

import yaml


class DefinitionManager(collections.Mapping):
    def __init__(self, directory: pathlib.Path):
        self.directory = directory

    def __getitem__(self, name):
        path = self.get_path_from_name(name)
        return self.get_yaml_from_file(path)

    def __iter__(self):
        for path in sorted(self.directory.glob('*.yml')):
            yield path.name[:-4]

    def __len__(self):
        return len(list(self))

    def get_path_from_name(self, name):
        return self.directory / (name + '.yml')

    def get_yaml_from_file(self, path):
        with path.open() as yaml_file:
            return yaml.load(yaml_file)
