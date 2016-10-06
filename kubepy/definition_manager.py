import pathlib

import yaml


class DefinitionManager:
    def __init__(self, directory: pathlib.Path):
        self.directory = directory

    def get_definition(self, name):
        path = self.directory / (name + '.yml')
        return self.get_yaml_from_file(path)

    def get_sorted_definitions(self):
        for path in sorted(self.directory.iterdir()):
            yield self.get_yaml_from_file(path)

    def get_yaml_from_file(self, path):
        with path.open() as yaml_file:
            return yaml.load(yaml_file)
