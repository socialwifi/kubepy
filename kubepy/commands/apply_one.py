#!/usr/bin/env python

import optparse
import pathlib

import yaml

from kubepy import appliers
from kubepy import appliers_options
from kubepy import base_commands


class InstallError(Exception):
    pass


class ApplyOneCommand(base_commands.BaseCommand):
    def get_optparser(self):
        parser = optparse.OptionParser(
            usage="usage: %prog [options] [job_name ...]",
            epilog="Installs or Executes selected definition",
        )
        parser.add_option(
            '--directory',
            dest='directories',
            action='append',
            help='installs definitions from this directory, can be defined multiple times to override definitions.',
        )
        parser.add_option(
            '--show-definition',
            dest='show_definition',
            action='store_true',
            default=False,
            help='shows definition instead of applying them.',
        )
        appliers_options.Options.add_applier_options(parser)
        return parser

    def handle(self, args, options):
        directory_strings = options.directories or ['.']
        directories = [pathlib.Path(directory_string).resolve() for directory_string in directory_strings]
        runner = appliers.DirectoriesApplier(directories, appliers_options.Options.from_parsed_options(options))
        if args:
            for job_name in args:
                if options.show_definition:
                    print(yaml.dump(runner.get_named_definition(job_name)))
                else:
                    runner.apply_named(job_name)
        else:
            raise base_commands.CommandError('Provide definition names.')


def run():
    ApplyOneCommand().run()


if __name__ == '__main__':
    run()
