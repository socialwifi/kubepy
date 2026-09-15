import pytest

from kubepy import appliers
from kubepy import appliers_options


def deployment_definition(namespace=None):
    definition = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {'name': 'web'},
        'spec': {
            'template': {
                'spec': {
                    'containers': [{'name': 'web', 'image': 'web'}],
                },
            },
        },
    }
    if namespace is not None:
        definition['metadata']['namespace'] = namespace
    return definition


class TestNamespaceResolution:
    def test_no_namespace_anywhere_is_none(self):
        applier = appliers.UniversalDefinitionApplier(
            deployment_definition(), appliers_options.Options())

        assert applier.get_applier().namespace is None

    def test_options_namespace_is_used_when_definition_has_none(self):
        applier = appliers.UniversalDefinitionApplier(
            deployment_definition(), appliers_options.Options(namespace='chosen-namespace'))

        assert applier.get_applier().namespace == 'chosen-namespace'

    def test_definition_namespace_wins_over_options(self):
        applier = appliers.UniversalDefinitionApplier(
            deployment_definition(namespace='explicit'), appliers_options.Options(namespace='chosen-namespace'))

        assert applier.get_applier().namespace == 'explicit'

    def test_applies_to_resource_kinds_too(self):
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {'name': 'api'},
            'spec': {'ports': [{'port': 80}]},
        }
        applier = appliers.UniversalDefinitionApplier(
            service, appliers_options.Options(namespace='chosen-namespace'))

        chosen = applier.get_applier()

        assert isinstance(chosen, appliers.ResourceApplier)
        assert chosen.namespace == 'chosen-namespace'


def pod_definition(name='check-migration'):
    return {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {'name': name},
        'spec': {
            'restartPolicy': 'Never',
            'containers': [{'name': 'check', 'image': 'check'}],
        },
    }


class TestPodApplierNamespaceInLogs:
    def test_failing_pod_looks_up_logs_in_resolved_namespace(self, monkeypatch):
        recorded_namespaces = []
        failed_status = {
            'containerStatuses': [
                {'name': 'check', 'state': {'terminated': {'reason': 'Error'}}},
            ],
        }
        monkeypatch.setattr(appliers.api, 'create', lambda definition, namespace=None: None)
        monkeypatch.setattr(appliers.api, 'get', lambda kind, name=None, namespace=None: {'status': failed_status})
        monkeypatch.setattr(appliers.api, 'delete', lambda kind, name, namespace=None: None)

        def fake_logs(pod_name, container_name=None, namespace=None):
            recorded_namespaces.append(namespace)
            return b'stdout', b'stderr'

        monkeypatch.setattr(appliers.api, 'logs', fake_logs)

        applier = appliers.UniversalDefinitionApplier(
            pod_definition(), appliers_options.Options(namespace='chosen-namespace')).get_applier()

        with pytest.raises(appliers.PodError):
            applier.apply()

        assert recorded_namespaces == ['chosen-namespace']


def named_definition(name, kind='Deployment'):
    return {'apiVersion': 'v1', 'kind': kind, 'metadata': {'name': name}}


# Keys are intentionally out of sorted order so the assertions below can distinguish
# "preserves the order it was given" from "sorts by key".
UNSORTED_MANAGER = {
    '03_migrate': named_definition('migrate', kind='Job'),
    '01_deployment': named_definition('web'),
    '02_service': named_definition('api', kind='Service'),
}


class TestDefinitionsToApply:
    manager = UNSORTED_MANAGER

    def test_without_skip_yields_everything_in_manager_order(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        names = [d['metadata']['name'] for d in applier.definitions_to_apply()]

        assert names == ['migrate', 'web', 'api']

    def test_skip_excludes_matching_definitions(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        names = [
            d['metadata']['name']
            for d in applier.definitions_to_apply(skip=lambda d: d['kind'] == 'Service')
        ]

        assert names == ['migrate', 'web']

    def test_skip_returning_false_for_everything_yields_everything(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        names = [d['metadata']['name'] for d in applier.definitions_to_apply(skip=lambda d: False)]

        assert names == ['migrate', 'web', 'api']

    def test_skip_everything_yields_nothing(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        assert list(applier.definitions_to_apply(skip=lambda d: True)) == []


class TestDefinitionsToSkip:
    manager = UNSORTED_MANAGER

    def test_nothing_skipped_yields_empty(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        assert list(applier.definitions_to_skip(skip=lambda d: False)) == []

    def test_selective_predicate_yields_only_matching_definitions(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        names = [
            d['metadata']['name']
            for d in applier.definitions_to_skip(skip=lambda d: d['kind'] == 'Service')
        ]

        assert names == ['api']

    def test_order_is_preserved(self):
        applier = appliers.DefinitionsApplier(self.manager, appliers_options.Options())

        names = [d['metadata']['name'] for d in applier.definitions_to_skip(skip=lambda d: True)]

        assert names == ['migrate', 'web', 'api']


class TestApplyAll:
    # Only kinds routed to ResourceApplier are used here so that apply_all() reaches api.apply
    # directly, without going through the Job/Pod appliers' create/poll/delete loop. Keys are
    # again out of sorted order, for the same reason as UNSORTED_MANAGER.
    manager = {
        '03_secret': named_definition('migrate', kind='Secret'),
        '01_service': named_definition('web', kind='Service'),
        '02_configmap': named_definition('api', kind='ConfigMap'),
    }

    def record_applied(self, monkeypatch):
        applied = []
        monkeypatch.setattr(appliers.api, 'apply', lambda definition, namespace=None: applied.append(
            (definition['metadata']['name'], namespace)))
        return applied

    def test_applies_everything_in_manager_order(self, monkeypatch):
        applied = self.record_applied(monkeypatch)

        appliers.DefinitionsApplier(self.manager, appliers_options.Options()).apply_all()

        assert applied == [('migrate', None), ('web', None), ('api', None)]

    def test_passes_options_namespace_through(self, monkeypatch):
        applied = self.record_applied(monkeypatch)

        appliers.DefinitionsApplier(
            self.manager, appliers_options.Options(namespace='chosen-namespace')).apply_all()

        assert applied == [
            ('migrate', 'chosen-namespace'),
            ('web', 'chosen-namespace'),
            ('api', 'chosen-namespace'),
        ]

    def test_skip_excludes_matching_definitions(self, monkeypatch):
        applied = self.record_applied(monkeypatch)

        appliers.DefinitionsApplier(self.manager, appliers_options.Options()).apply_all(
            skip=lambda d: d['kind'] == 'ConfigMap')

        assert applied == [('migrate', None), ('web', None)]
