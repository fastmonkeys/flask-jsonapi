class ResourceRegistry(object):
    def __init__(self):
        self.resources_by_type = {}
        self.resources_by_model = {}

    def add(self, resource_class):
        type = resource_class._meta.type
        model_class = resource_class._meta.model_class

        if type in self.resources_by_type:
            raise ImproperlyConfigured(
                'Cannot register another resource {another_resource!r} with '
                'the same type {type!r} as {existing_resource_class!r}.'.format(
                    type=type,
                    another_resource_class=resource_class,
                    existing_resource_class=self.resources_by_type[type]
                )
            )

        if model_class in self.resources_by_model:
            raise ImproperlyConfigured(
                'Cannot register another resource {another_resource!r} with '
                'the same model class {model_class!r} as '
                '{existing_resource_class!r}.'.format(
                    model_class=model_class,
                    another_resource_class=resource_class,
                    existing_resource_class=self.resources_by_type[type]
                )
            )

        self.resources_by_type[type] = resource_class
        self.resources_by_model[model_class] = resource_class
