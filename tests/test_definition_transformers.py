from kubepy import definition_transformers


class TestTagUntagedImages:
    def test_if_image_is_tagged(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }

        new_definition = definition_transformers.tag_untaged_images(definition, tag='dev')

        old_image = definition['spec']['template']['spec']['containers'][0]['image']
        new_image = new_definition['spec']['template']['spec']['containers'][0]['image']
        assert old_image == 'nginx'
        assert new_image == 'nginx:dev'

    def test_if_every_image_is_tagged(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                            {
                                'name': 'redis-container',
                                'image': 'redis',
                            },
                        ],
                    },
                },
            },
        }

        new_definition = definition_transformers.tag_untaged_images(definition, tag='dev')

        old_nginx_image = definition['spec']['template']['spec']['containers'][0]['image']
        new_nginx_image = new_definition['spec']['template']['spec']['containers'][0]['image']
        old_redis_image = definition['spec']['template']['spec']['containers'][1]['image']
        new_redis_image = new_definition['spec']['template']['spec']['containers'][1]['image']
        assert old_nginx_image == 'nginx'
        assert new_nginx_image == 'nginx:dev'
        assert old_redis_image == 'redis'
        assert new_redis_image == 'redis:dev'

    def test_if_already_tagged_image_is_skipped(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx:1.7.9',
                            },
                        ],
                    },
                },
            },
        }

        new_definition = definition_transformers.tag_untaged_images(definition, tag='dev')

        old_image = definition['spec']['template']['spec']['containers'][0]['image']
        new_image = new_definition['spec']['template']['spec']['containers'][0]['image']
        assert old_image == 'nginx:1.7.9'
        assert new_image == 'nginx:1.7.9'


class TestSetEnvironment:
    def test_if_environment_is_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        new_environment = {
            'DEBUG': 'true',
        }

        new_definition = definition_transformers.set_environment(definition, new_environment=new_environment)

        new_container_spec = new_definition['spec']['template']['spec']['containers'][0]
        assert 'env' in new_container_spec
        assert new_container_spec['env'] == [{
            'name': 'DEBUG',
            'value': 'true',
        }]

    def test_if_multiple_environment_values_are_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        new_environment = {
            'DEBUG': 'true',
            'CONFIGURATION': 'development',
        }

        new_definition = definition_transformers.set_environment(definition, new_environment=new_environment)

        new_container_environment = new_definition['spec']['template']['spec']['containers'][0]['env']
        assert len(new_container_environment) == 2
        assert {
            'name': 'DEBUG',
            'value': 'true',
        } in new_container_environment
        assert {
            'name': 'CONFIGURATION',
            'value': 'development',
        } in new_container_environment

    def test_if_every_container_has_environment_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                            {
                                'name': 'redis-container',
                                'image': 'redis',
                            },
                        ],
                    },
                },
            },
        }
        environment = {
            'DEBUG': 'true',
        }

        new_definition = definition_transformers.set_environment(definition, new_environment=environment)

        new_nginx_environment = new_definition['spec']['template']['spec']['containers'][0]['env']
        new_redis_environment = new_definition['spec']['template']['spec']['containers'][1]['env']
        assert new_nginx_environment == [{
            'name': 'DEBUG',
            'value': 'true',
        }]
        assert new_redis_environment == [{
            'name': 'DEBUG',
            'value': 'true',
        }]

    def test_if_existing_environment_is_updated(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                                'env': [{
                                    'name': 'DEBUG',
                                    'value': 'false',
                                }]
                            },
                        ],
                    },
                },
            },
        }
        new_environment = {
            'DEBUG': 'true',
        }

        new_definition = definition_transformers.set_environment(definition, new_environment=new_environment)

        old_environment = definition['spec']['template']['spec']['containers'][0]['env']
        assert old_environment == [{
            'name': 'DEBUG',
            'value': 'false',
        }]
        environment = new_definition['spec']['template']['spec']['containers'][0]['env']
        assert environment == [{
            'name': 'DEBUG',
            'value': 'true',
        }]

    def test_if_existing_environment_is_preserved(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                                'env': [{
                                    'name': 'DEBUG',
                                    'value': 'false',
                                }]
                            },
                        ],
                    },
                },
            },
        }
        new_environment = {
            'CONFIGURATION': 'development',
        }

        new_definition = definition_transformers.set_environment(definition, new_environment=new_environment)

        environment = new_definition['spec']['template']['spec']['containers'][0]['env']
        assert len(environment) == 2
        assert {
           'name': 'DEBUG',
           'value': 'false',
        } in environment
        assert {
           'name': 'CONFIGURATION',
           'value': 'development',
        } in environment


class TestAddHostVolumes:
    def test_if_volume_is_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        host_volumes = {
            'dev-volume': '/home',
        }

        new_definition = definition_transformers.add_host_volumes(definition, host_volumes=host_volumes)

        new_container_spec = new_definition['spec']['template']['spec']
        assert 'volumes' in new_container_spec
        assert new_container_spec['volumes'] == [{
            'name': 'dev-volume',
            'hostPath': {'path': '/home'},
        }]

    def test_if_multiple_volumes_are_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        host_volumes = {
            'dev-volume': '/home',
            'tmp-volume': '/tmp',
        }

        new_definition = definition_transformers.add_host_volumes(definition, host_volumes=host_volumes)

        new_volumes = new_definition['spec']['template']['spec']['volumes']
        assert len(new_volumes) == 2
        assert {
            'name': 'dev-volume',
            'hostPath': {'path': '/home'},
        } in new_volumes
        assert {
            'name': 'tmp-volume',
            'hostPath': {'path': '/tmp'},
        } in new_volumes


class TestAddLabels:
    def test_if_label_is_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        labels = {
            'app': 'nginx',
        }

        new_definition = definition_transformers.add_labels(definition, labels=labels)

        new_metadata = new_definition['spec']['template']['metadata']
        assert 'labels' in new_metadata
        assert new_metadata['labels'] == {
            'app': 'nginx',
        }

    def test_if_multiple_labels_are_set(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        labels = {
            'app': 'nginx',
            'tier': 'frontend',
        }

        new_definition = definition_transformers.add_labels(definition, labels=labels)

        new_labels = new_definition['spec']['template']['metadata']['labels']
        assert new_labels == {
            'app': 'nginx',
            'tier': 'frontend',
        }

    def test_with_existing_labels(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'nginx',
                            'tier': 'frontend',
                        }
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        labels = {
            'tier': 'backend',
            'track': 'canary',
        }

        new_definition = definition_transformers.add_labels(definition, labels=labels)

        new_labels = new_definition['spec']['template']['metadata']['labels']
        assert new_labels == {
            'app': 'nginx',
            'tier': 'backend',
            'track': 'canary',
        }


class TestIterateContainerDefinitions:
    def test_if_works_for_job(self):
        definition = {
            'kind': 'Job',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'python-container',
                                'image': 'python',
                            },
                        ],
                    },
                },
            },
        }
        containers = definition_transformers.iterate_container_definitions(definition)
        assert containers == [{'name': 'python-container', 'image': 'python'}]

    def test_if_works_for_deployment(self):
        definition = {
            'kind': 'Deployment',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        containers = definition_transformers.iterate_container_definitions(definition)
        assert containers == [{'name': 'nginx-container', 'image': 'nginx'}]

    def test_if_works_for_statefulset(self):
        definition = {
            'kind': 'StatefulSet',
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'name': 'nginx-container',
                                'image': 'nginx',
                            },
                        ],
                    },
                },
            },
        }
        containers = definition_transformers.iterate_container_definitions(definition)
        assert containers == [{'name': 'nginx-container', 'image': 'nginx'}]

    def test_if_works_for_pod(self):
        definition = {
            'kind': 'Pod',
            'spec': {
                'containers': [
                    {
                        'name': 'nginx-container',
                        'image': 'nginx',
                    },
                ],
            },
        }
        containers = definition_transformers.iterate_container_definitions(definition)
        assert containers == [{'name': 'nginx-container', 'image': 'nginx'}]
