import copy


def tag_untaged_images(definition, tag):
    new_definition = copy.deepcopy(definition)
    for container in iterate_container_definitions(new_definition):
        container['image'] = tag_untaged_image(container['image'], tag)
    return new_definition


def iterate_container_definitions(new_definition):
    crawler_class_map = {
        'Job': DefinitionWithPodTemplateCrawler,
        'Deployment': DefinitionWithPodTemplateCrawler,
        'Pod': PodCrawler,
    }
    crawler = crawler_class_map[new_definition['kind']](new_definition)
    return crawler.iterate_container_definitions()


class BaseCrawler:
    def __init__(self, definition):
        self.definition = definition

    def iterate_container_definitions(self):
        raise NotImplementedError


class DefinitionWithPodTemplateCrawler(BaseCrawler):
    def iterate_container_definitions(self):
        pod_crawler = PodCrawler(self.definition['spec']['template'])
        yield from pod_crawler.iterate_container_definitions()


class PodCrawler(BaseCrawler):
    def iterate_container_definitions(self):
        yield from self.definition['spec']['containers']


def tag_untaged_image(image, tag):
    if ':' in image:
        return image
    else:
        return image + ':' + tag
