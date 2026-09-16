import optparse

from kubepy import appliers_options


class TestNamespaceOption:
    def test_defaults_to_none(self):
        options = appliers_options.Options()

        assert options.namespace is None

    def test_accepts_explicit_namespace(self):
        options = appliers_options.Options(namespace='chosen-namespace')

        assert options.namespace == 'chosen-namespace'

    def test_other_defaults_are_unchanged(self):
        options = appliers_options.Options()

        assert options.build_tag == 'latest'
        assert options.replace is False
        assert options.labels == {}
        assert options.environment == {}
        assert options.max_job_retries is None

    def test_parsed_from_command_line(self):
        parser = optparse.OptionParser()
        appliers_options.Options.add_applier_options(parser)

        parsed, _ = parser.parse_args(['--namespace', 'chosen-namespace'])
        options = appliers_options.Options.from_parsed_options(parsed)

        assert options.namespace == 'chosen-namespace'

    def test_parsed_without_namespace_is_none(self):
        parser = optparse.OptionParser()
        appliers_options.Options.add_applier_options(parser)

        parsed, _ = parser.parse_args([])
        options = appliers_options.Options.from_parsed_options(parsed)

        assert options.namespace is None
