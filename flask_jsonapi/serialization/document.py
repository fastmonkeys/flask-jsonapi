from . import resource_identifier, resource_object


class _DocumentSerializer(object):
    def __init__(self, resource, fields=None, include=None):
        self.resource = resource
        self.fields = {} if fields is None else fields
        self.include = {} if include is None else include

    def dump(self):
        self._included_objects = set()

        document = {'data': self._dump_primary()}

        included = self._dump_included()
        if included:
            document['included'] = included

        return document

    def _dump_primary(self):
        raise NotImplementedError

    def _dump_included(self):
        return NotImplementedError

    def _dump_resource_object(self, resource, model):
        key = self._get_resource_object_key(resource=resource, model=model)
        if key not in self._included_objects:
            self._included_objects.add(key)
            return resource_object.dump(
                resource=resource,
                model=model,
                fields=self.fields.get(resource.type)
            )

    def _iter_included_objects(self, model):
        included_models = self._iter_included_models(
            resource=self.resource,
            model=model,
            include=self.include
        )
        for resource, model in included_models:
            obj = self._dump_resource_object(resource=resource, model=model)
            if obj is not None:
                yield obj

    @staticmethod
    def _get_resource_object_key(resource, model):
        data = resource_identifier.dump(resource=resource, model=model)
        return data['type'], data['id']

    def _iter_included_models(self, resource, model, include):
        for relationship_name in include:
            relationship = resource.relationships[relationship_name]
            related_models = self._iter_related_models(
                model=model,
                relationship=relationship
            )
            for related_model in related_models:
                yield relationship.resource, related_model
                included_models = self._iter_included_models(
                    resource=relationship.resource,
                    model=related_model,
                    include=include[relationship.name]
                )
                for included_model in included_models:
                    yield included_model

    @staticmethod
    def _iter_related_models(model, relationship):
        related = getattr(model, relationship.name)
        if relationship.many:
            for related_model in related:
                yield related_model
        elif related is not None:
            yield related
