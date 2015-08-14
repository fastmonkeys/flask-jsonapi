import itertools

from flask import url_for


class Serializer(object):
    def __init__(self, resource_registry, params, base_url=''):
        self.resource_registry = resource_registry
        self.params = params
        self.base_url = base_url

    def dump(self, input_):
        many = isinstance(input_, list)
        self._included_resource_objects = set()
        data = self._dump_primary_data(input_, many)
        included = self._dump_included_data(input_, many)
        document = {'data': data}
        if included:
            document['included'] = included
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
            'self': self._get_model_url(
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

    def _dump_relationship_object(self, model, relationship):
        resource = self._get_resource(model)
        related = resource.store.get_related(model, relationship)
        if resource.store.is_to_many_relationship(
            model.__class__,
            relationship
        ):
            data = [self._dump_resource_identifier(m) for m in related]
        else:
            data = self._dump_resource_identifier(related)
        return {
            "links": {
                "self": self._get_relationship_url(
                    type=resource.type,
                    id=resource.store.get_id(model),
                    relation=relationship
                ),
                "related": self._get_related_url(
                    type=resource.type,
                    id=resource.store.get_id(model),
                    relation=relationship
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
        for relationship in include:
            if store.is_to_many_relationship(
                model.__class__,
                relationship
            ):
                related_models = store.get_related(model, relationship)
                for related_model in related_models:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m
            else:
                related_model = store.get_related(model, relationship)
                if related_model is not None:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m

    def _get_collection_url(self, type):
        return '{base_url}/{type}'.format(base_url=self.base_url, type=type)

    def _get_model_url(self, type, id):
        return '{collection_url}/{id}'.format(
            collection_url=self._get_collection_url(type),
            id=id
        )

    def _get_related_url(self, type, id, relation):
        return '{model_url}/{relation}'.format(
            model_url=self._get_model_url(type, id),
            relation=relation
        )

    def _get_relationship_url(self, type, id, relation):
        return '{model_url}/relationships/{relation}'.format(
            model_url=self._get_model_url(type, id),
            relation=relation
        )
