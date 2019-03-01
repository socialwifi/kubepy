#!/usr/bin/env python
import optparse
import pathlib

from kubepy import appliers
from kubepy import appliers_options
from kubepy import base_commands


class InstallAllCommand(base_commands.BaseCommand):
    def handle(self, args, options):
        directory_strings = options.directories or ['.']
        directories = [pathlib.Path(directory_string).resolve() for directory_string in directory_strings]
        applier = appliers.DirectoriesApplier(directories, appliers_options.Options.from_parsed_options(options))
        applier.apply_all()

    def get_optparser(self):
        parser = optparse.OptionParser(
            usage="usage: %prog [options] [name ...]",
            epilog="Apply definitions from given directory.",
        )
        parser.add_option(
            '--directory',
            dest='directories',
            action='append',
            help='installs definitions from this directory, can be defined multiple times to override definitions.',
        )
        appliers_options.Options.add_applier_options(parser)
        return parser


def run():
    InstallAllCommand().run()


if __name__ == '__main__':
    run()
