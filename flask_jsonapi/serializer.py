import itertools

from . import link_builder


class Serializer(object):
    def __init__(self, resource_registry, params):
        self.resource_registry = resource_registry
        self.params = params

    def dump(self, input_, links=None):
        many = isinstance(input_, list)
        self._included_resource_objects = set()
        data = self._dump_primary_data(input_, many)
        included = self._dump_included_data(input_, many)
        document = {'data': data}
        if included:
            document['included'] = included
        if links:
            document['links'] = links
        return document

    def dump_relationship(self, input_, links=None):
        many = isinstance(input_, list)
        if many:
            data = [self._dump_resource_identifier(m) for m in input_]
        else:
            data = self._dump_resource_identifier(input_)
        document = {'data': data}
        if links:
            document['links'] = links
        return document

    def _dump_primary_data(self, input_, many):
        if many:
            return [self._dump_resource_object(model) for model in input_]
        elif input_ is None:
            return None
        else:
            return self._dump_resource_object(input_)

    def _dump_included_data(self, input_, many):
        if input_ is None:
            return []
        input_ = input_ if many else [input_]
        models = itertools.chain.from_iterable(
            self._iter_included_models(model, self.params.include.tree)
            for model in input_
        )
        return [
            self._dump_resource_object(model)
            for model in models
            if not self._has_already_been_included(model)
        ]

    def _dump_resource_object(self, model):
        resource = self._get_resource(model)
        identifier = (resource.type, resource.store.get_id(model))
        self._included_resource_objects.add(identifier)

        resource_object = {
            'id': resource.store.get_id(model),
            'type': resource.type,
        }

        attributes_object = self._dump_attributes_object(resource, model)
        if attributes_object:
            resource_object['attributes'] = attributes_object

        relationships_object = self._dump_relationships_object(resource, model)
        if relationships_object:
            resource_object['relationships'] = relationships_object

        resource_object['links'] = {
            'self': link_builder.build_individual_resource_url(
                type=resource_object['type'],
                id=resource_object['id']
            )
        }

        return resource_object

    def _get_resource(self, model):
        return self.resource_registry.by_model_class[model.__class__]

    def _dump_attributes_object(self, resource, model):
        fields = self.params.fields[resource.type]
        attributes = fields & set(resource.attributes)
        return {
            attr: resource.store.get_attribute(model, attr)
            for attr in attributes
        }

    def _dump_relationships_object(self, resource, model):
        fields = self.params.fields[resource.type]
        relationships = fields & set(resource.relationships)
        return {
            relationship: self._dump_relationship_object(model, relationship)
            for relationship in relationships
        }

    def _dump_relationship_object(self, model, relationship_name):
        resource = self._get_resource(model)
        relationship = resource.relationships[relationship_name]
        related = resource.store.get_related(model, relationship_name)
        if relationship.many:
            data = [self._dump_resource_identifier(m) for m in related]
        else:
            data = self._dump_resource_identifier(related)
        return {
            "links": {
                "self": link_builder.build_relationship_url(
                    type=resource.type,
                    id=resource.store.get_id(model),
                    relationship=relationship.name
                ),
                "related": link_builder.build_related_url(
                    type=resource.type,
                    id=resource.store.get_id(model),
                    relationship=relationship.name
                ),
            },
            "data": data
        }

    def _dump_resource_identifier(self, model):
        if model is not None:
            resource = self._get_resource(model)
            return {
                "type": resource.type,
                "id": resource.store.get_id(model)
            }

    def _has_already_been_included(self, model):
        resource = self._get_resource(model)
        identifier = (resource.type, resource.store.get_id(model))
        return identifier in self._included_resource_objects

    def _iter_included_models(self, model, include):
        resource = self._get_resource(model)
        store = resource.store
        for relationship_name in include:
            relationship = resource.relationships[relationship_name]
            if relationship.many:
                related_models = store.get_related(model, relationship.name)
                for related_model in related_models:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship.name]
                    ):
                        yield m
            else:
                related_model = store.get_related(model, relationship.name)
                if related_model is not None:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship.name]
                    ):
                        yield m
