import copy


def tag_untaged_images(definition, tag):
    new_definition = copy.deepcopy(definition)
    for container in iterate_container_definitions(new_definition):
        container['image'] = tag_untaged_image(container['image'], tag)
    return new_definition


def iterate_container_definitions(definition):
    new_spec = definition['spec']
    new_template = new_spec['template']
    yield from new_template['spec']['containers']


def tag_untaged_image(image, tag):
    if ':' in image:
        return image
    else:
        return image + ':' + tag
