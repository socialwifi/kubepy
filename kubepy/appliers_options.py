def parse_dict_options_callback(option, opt_str, value, parser):
    name, path = value.split('=', 1)
    getattr(parser.values, option.dest)[name] = path


class Options:
    PARSER_CONFIGURATION = [
        ('--build-tag', {
            'dest': 'build_tag', 'action': 'store', 'help': 'used image tag and name suffix',
        }),
        ('--label', {
            'dest': 'labels',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add label to definition. Format is key=value. Can be used multiple times.',
        }),
        ('--label-pod', {
            'dest': 'pod_labels',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add label to each pod definition. Format is key=value. Can be used multiple times.',
        }),
        ('--annotate', {
            'dest': 'annotations',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add annotation to definition. Format is key=value. Can be used multiple times.',
        }),
        ('--annotate-pod', {
            'dest': 'pod_annotations',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add annotation to each pod definition. Format is key=value. Can be used multiple times.',
        }),
        ('--replace', {
            'dest': 'replace',
            'action': 'store_true',
            'help': 'delete and recreate deployments instead of doing rolling update',
        }),
        ('--host-volume', {
            'dest': 'host_volumes',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add host volume to pods. Format is name=path  (--host-volume=dev-volume=/home)',
        }),
        ('--env', {
            'dest': 'environment',
            'action': 'callback',
            'type': 'string',
            'callback': parse_dict_options_callback,
            'help': 'add environment variable to containers. Format is VAR=value  (--env=BUILD_NUMBER=2)',
        }),
        ('--max-job-retries', {
            'dest': 'max_job_retries',
            'action': 'store',
            'type': 'int',
            'help': 'When applying job fail if job fails n times.',
        }),
    ]

    def __init__(self, *, build_tag='latest', labels=None, pod_labels=None, annotations=None, pod_annotations=None,
                 replace=False, host_volumes=None, environment=None, max_job_retries=None):
        self.build_tag = build_tag
        self.labels = labels or {}
        self.pod_labels = pod_labels or {}
        self.annotations = annotations or {}
        self.pod_annotations = pod_annotations or {}
        self.replace = replace
        self.host_volumes = host_volumes or {}
        self.environment = environment or {}
        self.max_job_retries = max_job_retries

    @classmethod
    def add_applier_options(cls, parser):
        default_options = cls()
        for option, option_kwargs in cls.PARSER_CONFIGURATION:
            attribute = option_kwargs['dest']
            parser.add_option(option, default=getattr(default_options, attribute), **option_kwargs)

    @classmethod
    def from_parsed_options(cls, parsed_options):
        kwargs = {}
        for _, option_kwargs in cls.PARSER_CONFIGURATION:
            attribute = option_kwargs['dest']
            kwargs[attribute] = getattr(parsed_options, attribute)
        return cls(**kwargs)
