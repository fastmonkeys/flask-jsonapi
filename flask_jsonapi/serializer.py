from collections import defaultdict
import itertools

from flask import url_for


class Serializer(object):
    def __init__(self, resource_registry, params):
        self._resource_registry = resource_registry
        self._params = params

    def dump(self, input_, many=False):
        self._included_resource_objects = set()
        data = self._dump_primary_data(input_, many)
        included = self._dump_included_data(input_, many)
        document = {
            "data": data
        }
        if included:
            document["included"] = included
        return document

    def _dump_primary_data(self, input_, many):
        if many:
            return [self._dump_resource_object(model) for model in input_]
        else:
            return self._dump_resource_object(input_)

    def _dump_included_data(self, input_, many):
        input_ = input_ if many else [input_]
        models = itertools.chain.from_iterable(
            self._iter_included_models(model, self._params.include.tree)
            for model in input_
        )
        return [
            self._dump_resource_object(model)
            for model in models
            if not self._has_already_been_included(model)
        ]

    def _dump_resource_object(self, model):
        resource = self._get_resource(model)
        identifier = (resource.type, resource.repository.get_id(model))
        self._included_resource_objects.add(identifier)

        resource_object = {
            "id": resource.repository.get_id(model),
            "type": resource.type,
        }

        attributes_object = self._dump_attributes_object(resource, model)
        if attributes_object:
            resource_object["attributes"] = attributes_object

        relationships_object = self._dump_relationships_object(resource, model)
        if relationships_object:
            resource_object["relationships"] = relationships_object

        resource_object["links"] = {
            "self": url_for(
                'jsonapi.get',
                type=resource_object["type"],
                id=resource_object["id"]
            )
        }

        return resource_object

    def _get_resource(self, model):
        return self._resource_registry.by_model_class[model.__class__]

    def _dump_attributes_object(self, resource, model):
        attributes = self._params.fields[resource.type] & resource.attributes
        return {
            attr: resource.repository.get_attribute(model, attr)
            for attr in attributes
        }

    def _dump_relationships_object(self, resource, model):
        relationships = (
            self._params.fields[resource.type] &
            resource.relationships
        )
        return {
            relationship: self._dump_relationship_object(model, relationship)
            for relationship in relationships
        }

    def _dump_relationship_object(self, model, relationship):
        resource = self._get_resource(model)
        related = resource.repository.get_related(model, relationship)
        if resource.repository.is_to_many_relationship(model.__class__, relationship):
            data = [self._dump_resource_identifier(m) for m in related]
        else:
            data = self._dump_resource_identifier(related)
        return {
            "links": {
                "self": url_for(
                    'jsonapi.get_relationship',
                    type=resource.type,
                    id=resource.repository.get_id(model),
                    relationship=relationship
                ),
                "related": url_for(
                    'jsonapi.get_related',
                    type=resource.type,
                    id=resource.repository.get_id(model),
                    relationship=relationship
                ),
            },
            "data": data
        }

    def _dump_resource_identifier(self, model):
        if model is not None:
            resource = self._get_resource(model)
            return {
                "type": resource.type,
                "id": resource.repository.get_id(model)
            }

    def _has_already_been_included(self, model):
        resource = self._get_resource(model)
        identifier = (resource.type, resource.repository.get_id(model))
        return identifier in self._included_resource_objects

    def _iter_included_models(self, model, include):
        resource = self._get_resource(model)
        repository = resource.repository
        for relationship in include:
            if repository.is_to_many_relationship(model.__class__, relationship):
                related_models = repository.get_related(model, relationship)
                for related_model in related_models:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m
            else:
                related_model = repository.get_related(model, relationship)
                if related_model is not None:
                    yield related_model
                    for m in self._iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m
