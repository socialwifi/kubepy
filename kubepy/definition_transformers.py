import copy


def tag_untaged_images(definition, tag):
    new_definition = copy.deepcopy(definition)
    for container in iterate_container_definitions(new_definition):
        container['image'] = tag_untaged_image(container['image'], tag)
    return new_definition


def set_environment(definition, new_environment):
    new_definition = copy.deepcopy(definition)
    for container in iterate_container_definitions(new_definition):
        env_definition = container.get('env', [])
        env_definition = [
            env for env in env_definition if env['name'] not in new_environment.keys()
        ]
        for name, value in new_environment.items():
            env_definition.append({'name': name, 'value': value})
        container['env'] = env_definition
    return new_definition


def iterate_container_definitions(new_definition):
    return get_crawler(new_definition).get_container_definitions()


def add_host_volumes(definition, host_volumes):
    new_definition = copy.deepcopy(definition)
    for name, path in host_volumes.items():
        volumes = get_crawler(new_definition).get_volume_definitions()
        volumes.append({'name': name, 'hostPath': {'path': str(path)}})
    return new_definition


def add_labels(definition, labels, pod_labels):
    new_definition = copy.deepcopy(definition)
    crawler = get_crawler(new_definition)
    add_labels_to_metadata(metadata=crawler.get_metadata_definition(), labels=labels)
    add_labels_to_metadata(metadata=crawler.get_pod_metadata_definition(), labels=pod_labels)
    return new_definition


def add_labels_to_metadata(metadata, labels):
    new_labels = metadata.get('labels', {})
    for name, value in labels.items():
        new_labels[name] = value
    metadata['labels'] = new_labels


def add_annotations(definition, annotations, pod_annotations):
    new_definition = copy.deepcopy(definition)
    crawler = get_crawler(new_definition)
    add_annotations_to_metadata(metadata=crawler.get_metadata_definition(), annotations=annotations)
    add_annotations_to_metadata(metadata=crawler.get_pod_metadata_definition(), annotations=pod_annotations)
    return new_definition


def add_annotations_to_metadata(metadata, annotations):
    new_annotations = metadata.get('annotations', {})
    for name, value in annotations.items():
        new_annotations[name] = value
    metadata['annotations'] = new_annotations


def get_crawler(definition):
    return CRAWLER_CLASS_MAP[definition['kind']](definition)


class BaseCrawler:
    def __init__(self, definition):
        self.definition = definition

    def get_container_definitions(self):
        return self.get_pod_spec()['containers']

    def get_volume_definitions(self):
        return self.get_pod_spec().setdefault('volumes', [])

    def get_metadata_definition(self):
        return self.definition.setdefault('metadata', {})

    def get_pod_metadata_definition(self):
        return self.get_pod_metadata()

    def get_pod_spec(self):
        raise NotImplementedError

    def get_pod_metadata(self):
        raise NotImplementedError


class CronJobCrawler(BaseCrawler):
    def get_pod_spec(self):
        return self.get_job_crawler().get_pod_spec()

    def get_pod_metadata(self):
        return self.get_job_crawler().get_pod_metadata()

    def get_job_crawler(self):
        return DefinitionWithPodTemplateCrawler(self.definition['spec']['jobTemplate'])


class DefinitionWithPodTemplateCrawler(BaseCrawler):
    def get_pod_spec(self):
        return self.get_pod_crawler().get_pod_spec()

    def get_pod_metadata(self):
        return self.get_pod_crawler().get_pod_metadata()

    def get_pod_crawler(self):
        return PodCrawler(self.definition['spec']['template'])


class PodCrawler(BaseCrawler):
    def get_pod_spec(self):
        return self.definition['spec']

    def get_pod_metadata(self):
        return self.definition.setdefault('metadata', {})


def tag_untaged_image(image, tag):
    if ':' in image:
        return image
    else:
        return image + ':' + tag


CRAWLER_CLASS_MAP = {
    'Job': DefinitionWithPodTemplateCrawler,
    'CronJob': CronJobCrawler,
    'Deployment': DefinitionWithPodTemplateCrawler,
    'StatefulSet': DefinitionWithPodTemplateCrawler,
    'Pod': PodCrawler,
}
