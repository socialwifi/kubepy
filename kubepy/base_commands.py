import sys


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
