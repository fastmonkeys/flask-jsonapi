from flask import json

from . import errors, exceptions
from .params import Parameters
from .serializer import Serializer


class Controller(object):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    def fetch(self, type, params):
        resource = self._get_resource(type)
        params = self._build_params(type, params)
        count = resource.store.count(resource.model_class)
        objs = resource.store.fetch(resource.model_class, params)
        return self._serialize(objs, params)

    def fetch_one(self, type, id, params):
        resource = self._get_resource(type)
        params = self._build_params(type, params)
        obj = self._fetch_object(resource, id, params)
        return self._serialize(obj, params)

    def fetch_related(self, type, id, relation, params):
        resource = self._get_resource(type)
        related_resource = self._get_related_resource(resource, relation)
        params = self._build_params(related_resource.type, params)
        obj = self._fetch_object(resource, id)
        related = resource.store.fetch_related(obj, relation, params)
        return self._serialize(related, params)

    def _fetch_object(self, resource, id, params=None):
        try:
            return resource.store.fetch_one(resource.model_class, id, params)
        except exceptions.ObjectNotFound:
            raise errors.ResourceNotFound(id)

    def _get_resource(self, type):
        try:
            return self.resource_registry.by_type[type]
        except KeyError:
            raise errors.InvalidResource(type)

    def _get_related_resource(self, resource, relation):
        try:
            related_model_class = resource.store.get_related_model_class(
                resource.model_class,
                relation
            )
        except exceptions.InvalidRelationship:
            raise errors.RelationshipNotFound(resource.type, relation)
        return self.resource_registry.by_model_class[related_model_class]

    def _build_params(self, type, params):
        return Parameters(self.resource_registry, type, params)

    def _serialize(self, input, params):
        serializer = Serializer(self.resource_registry, params)
        return json.dumps(serializer.dump(input))
