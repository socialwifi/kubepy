import copy


def tag_untaged_images(definition, tag):
    new_definition = copy.deepcopy(definition)
    for container in iterate_container_definitions(new_definition):
        container['image'] = tag_untaged_image(container['image'], tag)
    return new_definition


def iterate_container_definitions(new_definition):
    return get_crawler(new_definition).get_container_definitions()


def add_host_volumes(definition, host_volumes):
    new_definition = copy.deepcopy(definition)
    for name, path in host_volumes.items():
        volumes = get_crawler(new_definition).get_volume_definitions()
        volumes.append({'name': name, 'hostPath': {'path': str(path)}})
    return new_definition


def get_crawler(definition):
    return CRAWLER_CLASS_MAP[definition['kind']](definition)


class BaseCrawler:
    def __init__(self, definition):
        self.definition = definition

    def get_container_definitions(self):
        return self.get_pod_spec()['containers']

    def get_volume_definitions(self):
        return self.get_pod_spec().setdefault('volumes', [])

    def get_pod_spec(self):
        raise NotImplementedError


class DefinitionWithPodTemplateCrawler(BaseCrawler):
    def get_pod_spec(self):
        return self.get_pod_crawler().get_pod_spec()

    def get_pod_crawler(self):
        return PodCrawler(self.definition['spec']['template'])


class PodCrawler(BaseCrawler):


    def get_pod_spec(self):
        return self.definition['spec']


def tag_untaged_image(image, tag):
    if ':' in image:
        return image
    else:
        return image + ':' + tag


CRAWLER_CLASS_MAP = {
    'Job': DefinitionWithPodTemplateCrawler,
    'Deployment': DefinitionWithPodTemplateCrawler,
    'Pod': PodCrawler,
}
