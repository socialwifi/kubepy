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
