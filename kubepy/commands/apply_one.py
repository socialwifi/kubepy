#!/usr/bin/env python

import optparse
import pathlib

from kubepy import appliers
from kubepy import base_commands


class InstallError(Exception):
    pass


class ApplyOneCommand(base_commands.BaseCommand):
    def get_optparser(self):
        parser = optparse.OptionParser(
            usage="usage: %prog [options] [job_name ...]",
            epilog="Installs or Executes selected definition"
        )
        parser.add_option(
            '--directory', dest='directory', default='.',
            help='installs definitions from this directory')
        base_commands.add_container_options(parser)
        return parser

    def handle(self, args, options):
        directory = pathlib.Path(options.directory).resolve()
        runner = appliers.DirectoryApplier(directory, options)
        if args:
            for job_name in args:
                runner.apply_named(job_name)
        else:
            raise base_commands.CommandError('Provide definition names.')


def run():
    ApplyOneCommand().run()

if __name__ == '__main__':
    run()
