from . import exceptions


class ResourceRegistry(object):
    def __init__(self):
        self.by_type = {}

    def register(self, resource):
        if resource.type in self.by_type:
            raise exceptions.ResourceAlreadyRegistered(
                'A resource with type {type!r} has already been '
                'registered.'.format(type=resource.type)
            )

        resource.register(self)
        self.by_type[resource.type] = resource
