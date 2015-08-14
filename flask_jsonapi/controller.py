import jsonschema
import qstring
from flask import current_app, json, request

from . import errors, exceptions, schemas
from .params import Parameters
from .serializer import Serializer


class Controller(object):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    def fetch(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        instances = resource.store.fetch(resource.model_class, params)
        return self._serialize(instances, params)

    def fetch_one(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)
        instance = self._fetch_object(resource, id, params)
        return self._serialize(instance, params)

    def fetch_related(self, type, id, relation):
        resource = self._get_resource(type)
        related_resource = self._get_related_resource(resource, relation)
        params = self._build_params(related_resource.type)
        instance = self._fetch_object(resource, id)
        related = resource.store.fetch_related(instance, relation, params)
        return self._serialize(related, params)

    def create(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        payload = self._get_json()
        self._validate_create_request(resource, payload)
        id = payload['data'].get('id')
        try:
            instance = resource.store.create(
                model_class=resource.model_class,
                id=id,
                fields=self._parse_fields(resource, payload)
            )
        except exceptions.ObjectAlreadyExists:
            raise errors.ResourceAlreadyExists(type=type, id=id)
        return current_app.response_class(
            response=self._serialize(obj, params),
            status=201
        )

    def _parse_fields(self, resource, payload):
        data = payload['data']
        fields = {}
        fields.update(data.get('attributes', {}))
        fields.update(
            self._parse_relationships(
                resource=resource,
                relationships=data.get('relationships', {})
            )
        )
        return fields

    def _validate_create_request(self, resource, payload):
        schema = schemas.get_create_request_schema(resource)
        self._validate(payload, schema)
        data = payload['data']
        type_ = data['type']
        if type_ != resource.type:
            raise errors.TypeMismatch(type_)
        if 'id' in data and not resource.allow_client_generated_ids:
            raise errors.ClientGeneratedIDsUnsupported(type_)

    def _parse_relationships(self, resource, relationships):
        return {
            relationship: self._parse_relationship(
                resource=resource,
                relationship=relationship,
                data=value['data']
            )
            for relationship, value in relationships.items()
        }

    def _parse_relationship(self, resource, relationship, data):
        related_resource = resource.get_related_resource(relationship)
        if relationship in resource.to_one_relationships:
            return self._parse_linkage(related_resource, linkage=data)
        else:
            return self._parse_linkages(related_resource, linkages=data)

    def _parse_linkage(self, related_resource, linkage):
        if linkage is not None:
            assert linkage['type'] == related_resource.type
            return related_resource.store.fetch_one(
                model_class=related_resource.model_class,
                id=linkage['id']
            )

    def _parse_linkages(self, related_resource, linkages):
        return [
            self._parse_linkage(related_resource, linkage)
            for linkage in linkages
        ]

    def _validate(self, payload, schema):
        try:
            jsonschema.validate(payload, schema)
        except jsonschema.ValidationError as e:
            raise errors.ValidationError(detail=e.message, path=e.path)

    def _get_json(self):
        json = request.get_json(force=True, silent=True)
        if json is None:
            raise errors.InvalidJSON
        return json

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
            return resource.get_related_resource(relation)
        except exceptions.InvalidRelationship:
            raise errors.RelationshipNotFound(resource.type, relation)

    def _build_params(self, type):
        return Parameters(
            resource_registry=self.resource_registry,
            type=type,
            params=qstring.nest(request.args.items(multi=True))
        )

    def _serialize(self, input, params):
        serializer = Serializer(self.resource_registry, params)
        return json.dumps(serializer.dump(input))
