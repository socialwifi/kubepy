import sys

from kubepy import definition_transformers


class CommandError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class BaseCommand:
    def run(self):
        parser = self.get_optparser()
        (options, names) = parser.parse_args()
        try:
            self.handle(names, options)
        except CommandError as e:
            print(e.message)
            parser.print_usage()
            sys.exit(1)

    def handle(self, args, options):
        raise NotImplementedError

    def get_optparser(self):
        raise NotImplementedError


def add_container_options(parser):
    parser.add_option(
        '--build-tag', dest='build_tag', action='store', default='latest',
        help='used image tag and name suffix')
    parser.add_option(
        '--replace', dest='replace', action='store_true', default=False,
        help='delete and recreate deployments instead of doing rolling update')
