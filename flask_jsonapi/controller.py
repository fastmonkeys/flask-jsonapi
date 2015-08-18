import jsonschema
import qstring
from flask import current_app, json, request
try:
    from sqlalchemy_json_api import QueryBuilder
except ImportError:
    QueryBuilder = None

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

    def fetch_related(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        params = self._build_params(relationship.type)
        instance = self._fetch_object(resource, id)
        related = resource.store.fetch_related(instance, relationship.name, params)
        return self._serialize(related, params)

    def fetch_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        params = self._build_params(relationship.type)
        instance = self._fetch_object(resource, id)
        related = resource.store.fetch_related(instance, relationship.name, params)
        return self._serialize_relationship(related, params)

    def create(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        payload = self._get_json()
        self._validate_create_request(resource, payload)
        data = payload['data']
        id = data.get('id')
        try:
            instance = resource.store.create(
                model_class=resource.model_class,
                id=id,
                fields=self._parse_fields(resource, data)
            )
        except exceptions.ObjectAlreadyExists:
            raise errors.ResourceAlreadyExists(type=type, id=id)
        return current_app.response_class(
            response=self._serialize(instance, params),
            status=201
        )

    def update(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)
        instance = self._fetch_object(resource, id)
        payload = self._get_json()
        self._validate_update_request(resource, id, payload)
        resource.store.update(
            instance=instance,
            fields=self._parse_fields(
                resource=resource,
                data=payload['data']
            )
        )
        return self._serialize(instance, params)

    def delete(self, type, id):
        resource = self._get_resource(type)
        try:
            instance = resource.store.fetch_one(resource.model_class, id)
        except exceptions.ObjectNotFound:
            pass
        else:
            resource.store.delete(instance)
        return current_app.response_class(response='', status=204)

    def create_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        instance = self._fetch_object(resource, id)
        if not relationship.many:
            abort(405)
        payload = self._get_json()
        self._validate_update_relationship_request(relationship, payload)
        resource.store.create_relationship(
            instance=instance,
            relationship=relationship.name,
            values=self._parse_relationship(
                resource=resource,
                relationship=relationship,
                data=payload['data'],
                path=['data']
            )
        )
        return current_app.response_class(response='', status=204)

    def update_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        instance = self._fetch_object(resource, id)
        payload = self._get_json()
        self._validate_update_relationship_request(relationship, payload)
        self._check_full_replacement(relationship, path=None)
        resource.store.update(
            instance=instance,
            fields={
                relationship.name: self._parse_relationship(
                    resource=resource,
                    relationship=relationship,
                    data=payload['data'],
                    path=['data'],
                )
            }
        )
        return current_app.response_class(response='', status=204)

    def delete_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        instance = self._fetch_object(resource, id)
        if not relationship.many:
            abort(405)
        payload = self._get_json()
        self._validate_update_relationship_request(relationship, payload)
        resource.store.delete_relationship(
            instance=instance,
            relationship=relationship.name,
            values=self._parse_relationship(
                resource=resource,
                relationship=relationship,
                data=payload['data'],
                path=['data'],
                ignore_not_found=True
            )
        )
        return current_app.response_class(response='', status=204)

    def _parse_fields(self, resource, data):
        fields = {}
        fields.update(data.get('attributes', {}))
        fields.update(
            self._parse_relationships(
                resource=resource,
                relationships=data.get('relationships', {}),
                path=['data', 'relationships']
            )
        )
        return fields

    def _validate_create_request(self, resource, payload):
        schema = schemas.get_create_request_schema(resource)
        self._validate(payload, schema)
        data = payload['data']
        type_ = data['type']
        if type_ != resource.type:
            raise errors.TypeMismatch(type_, path=['data', 'type'])
        if 'id' in data and not resource.allow_client_generated_ids:
            raise errors.ClientGeneratedIDsUnsupported(type_)

    def _validate_update_request(self, resource, id, payload):
        schema = schemas.get_update_request_schema(resource)
        self._validate(payload, schema)
        data = payload['data']
        if data['type'] != resource.type:
            raise errors.TypeMismatch(data['type'], path=['data', 'type'])
        if data['id'] != id:
            raise errors.IDMismatch(data['id'])

    def _validate_update_relationship_request(self, relationship, payload):
        schema = schemas.get_update_relationship_request_schema(relationship)
        self._validate(payload, schema)

    def _parse_relationships(self, resource, relationships, path):
        relationships = [
            (resource.relationships[relationship_name], value)
            for relationship_name, value in relationships.items()
        ]
        for relationship, _ in relationships:
            self._check_full_replacement(
                relationship=relationship,
                path=path + [relationship.name]
            )
        return {
            relationship.name: self._parse_relationship(
                resource=resource,
                relationship=relationship,
                data=value['data'],
                path=path + [relationship.name, 'data']
            )
            for relationship, value in relationships
        }

    def _check_full_replacement(self, relationship, path):
        if relationship.many and not relationship.allow_full_replacement:
            raise errors.FullReplacementDisallowed(
                relationship=relationship.name,
                path=path
            )

    def _parse_relationship(
        self, resource, relationship, data, path, ignore_not_found=False
    ):
        if relationship.many:
            return self._parse_linkages(
                relationship,
                linkages=data,
                path=path,
                ignore_not_found=ignore_not_found
            )
        else:
            return self._parse_linkage(relationship, linkage=data, path=path)

    def _parse_linkage(self, relationship, linkage, path):
        if linkage is not None:
            if linkage['type'] != relationship.type:
                raise errors.TypeMismatch(
                    type=linkage['type'],
                    path=path + ['type']
                )
            return self._fetch_object(
                resource=relationship.resource,
                id=linkage['id'],
                path=path
            )

    def _parse_linkages(
        self, relationship, linkages, path, ignore_not_found=False
    ):
        objs = []
        for i, linkage in enumerate(linkages):
            try:
                obj = self._parse_linkage(relationship, linkage, path + [i])
            except errors.ResourceNotFound:
                if not ignore_not_found:
                    raise
            else:
                objs.append(obj)
        return objs

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

    def _fetch_object(self, resource, id, params=None, path=None):
        try:
            return resource.store.fetch_one(resource.model_class, id, params)
        except exceptions.ObjectNotFound:
            raise errors.ResourceNotFound(type=resource.type, id=id, path=path)

    def _get_resource(self, type):
        try:
            return self.resource_registry.by_type[type]
        except KeyError:
            raise errors.InvalidResource(type)

    def _get_relationship(self, resource, relationship_name):
        try:
            return resource.relationships[relationship_name]
        except KeyError:
            raise errors.RelationshipNotFound(resource.type, relationship_name)

    def _build_params(self, type):
        return Parameters(
            resource_registry=self.resource_registry,
            type=type,
            params=qstring.nest(request.args.items(multi=True))
        )

    def _serialize(self, input, params):
        serializer = Serializer(self.resource_registry, params)
        return json.dumps(serializer.dump(input))

    def _serialize_relationship(self, input, params):
        serializer = Serializer(self.resource_registry, params)
        return json.dumps(serializer.dump_relationship(input))


class PostgreSQLController(Controller):
    def __init__(self, resource_registry):
        if QueryBuilder is None:
            raise ImportError(
                'PostgreSQLController needs SQLAlchemy-JSON-API installed.'
            )
        self.resource_registry = resource_registry

    @property
    def query_builder(self):
        return QueryBuilder({
            type: resource.model_class
            for type, resource in self.resource_registry.by_type.items()
        })

    def _get_query(self, resource, params):
        store = resource.store
        return store._paginate(
            store.query(resource.model_class),
            params.pagination
        )

    def fetch_one(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)
        include = params.include.raw
        query = self.query_builder.select_one(
            resource.model_class,
            id,
            include=include.split(',') if include else None,
            fields=params.fields,
            from_obj=resource.store.query(resource.model_class),
            as_text=True
        )
        result = resource.store.session.execute(query).scalar()
        if result == '{"data":null}':
            raise errors.ResourceNotFound(type, id)
        return result

    def fetch(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        include = params.include.raw
        query = self.query_builder.select(
            resource.model_class,
            include=include.split(',') if include else None,
            fields=params.fields,
            from_obj=self._get_query(resource, params),
            as_text=True
        )
        return resource.store.session.execute(query).scalar()

    def fetch_related(self, type, id, relation):
        resource = self._get_resource(type)
        try:
            related_resource = resource.relationships[relation]
        except KeyError:
            raise errors.RelationshipNotFound(resource.type, relation)
        params = self._build_params(related_resource.type)
        relationship = resource.store._get_relationship_property(
            resource.model_class,
            relation
        )

        obj = self._fetch_object(resource, id)
        include = params.include.raw
        query = self.query_builder.select(
            related_resource.model_class,
            include=include.split(',') if include else None,
            fields=params.fields,
            as_text=True,
            multiple=relationship.uselist,
            from_obj=resource.store._paginate(
                resource.store._query_related(obj, relation),
                params.pagination
            )
        )
        return resource.store.session.execute(query).scalar()
