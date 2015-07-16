class ResourceRegistry(object):
    def __init__(self):
        self.by_type = {}
        self.by_model = {}

    def register(self, resource_class):
        type = resource_class._meta.type
        model_class = resource_class._meta.model_class

        if type in self.by_type:
            raise ImproperlyConfigured(
                'Cannot register another resource {another_resource!r} with '
                'the same type {type!r} as {existing_resource_class!r}.'.format(
                    type=type,
                    another_resource_class=resource_class,
                    existing_resource_class=self.by_type[type]
                )
            )

        if model_class in self.by_model:
            raise ImproperlyConfigured(
                'Cannot register another resource {another_resource!r} with '
                'the same model class {model_class!r} as '
                '{existing_resource_class!r}.'.format(
                    model_class=model_class,
                    another_resource_class=resource_class,
                    existing_resource_class=self.by_type[type]
                )
            )

        resource_class.register(self)
        self.by_type[type] = resource_class
        self.by_model[model_class] = resource_class
