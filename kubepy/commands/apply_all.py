#!/usr/bin/env python
import optparse
import pathlib

from kubepy import appliers
from kubepy import base_commands


class InstallAllCommand(base_commands.BaseCommand):
    def handle(self, args, options):
        directory = pathlib.Path(options.directory).resolve()
        applier = appliers.DirectoryApplier(directory, options)
        applier.apply_all()

    def get_optparser(self):
        parser = optparse.OptionParser(
            usage="usage: %prog [options] [name ...]",
            epilog="Apply definitions from given directory."
        )
        parser.add_option(
            '--directory', dest='directory', default='.',
            help='installs all definitions from this directory')
        base_commands.add_container_options(parser)
        return parser


def run():
    InstallAllCommand().run()


if __name__ == '__main__':
    run()
