from . import exceptions


class ResourceRegistry(object):
    def __init__(self):
        self.by_type = {}
        self.by_model_class = {}

    def register(self, resource):
        if resource.type in self.by_type:
            raise exceptions.ResourceAlreadyRegistered(
                'A resource with type {type!r} has already been '
                'registered.'.format(type=resource.type)
            )

        if resource.model_class in self.by_model_class:
            raise exceptions.ResourceAlreadyRegistered(
                'A resource with model class {model_class!r} has already been '
                'registered.'.format(model_class=resource.model_class)
            )

        self.by_type[resource.type] = resource
        self.by_model_class[resource.model_class] = resource
