from flask import abort, current_app, json, request
from werkzeug.urls import url_encode

import jsonschema
import qstring

from .. import errors, exceptions, link_builder, schemas
from ..params import Parameters
from ..serializer import Serializer


class DefaultController(object):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    def fetch(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        instances = resource.store.fetch(resource.model_class, params)
        count = resource.store.count(resource.model_class)
        links = self._get_links(params, count)
        return self._serialize(instances, params, links)

    def fetch_one(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)
        instance = self._fetch_object(resource, id, params)
        links = self._get_links(params)
        return self._serialize(instance, params, links)

    def fetch_related(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        params = self._build_params(relationship.type)
        instance = self._fetch_object(resource, id)
        related = resource.store.fetch_related(
            instance=instance,
            relationship=relationship.name,
            params=params
        )
        if relationship.many:
            count = resource.store.count_related(instance, relationship.name)
        else:
            count = None
        links = self._get_links(params, count)
        return self._serialize(related, params, links)

    def fetch_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        params = self._build_params(relationship.type)
        instance = self._fetch_object(resource, id)
        related = resource.store.fetch_related(
            instance=instance,
            relationship=relationship.name,
            params=params
        )
        if relationship.many:
            count = resource.store.count_related(instance, relationship.name)
        else:
            count = None
        links = self._get_links(params, count)
        links['related'] = link_builder.build_related_url(
            type=type,
            id=id,
            relationship=relationship.name
        )
        return self._serialize_relationship(related, params, links)

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
        links = {
            'self': link_builder.build_individual_resource_url(
                type=type,
                id=resource.store.get_id(instance)
            )
        }
        return current_app.response_class(
            response=self._serialize(instance, params, links),
            status=201,
            headers={'Location': links['self']}
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
        links = self._get_links(params)
        return self._serialize(instance, params, links)

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
                source_pointer='/data'
            )
        )
        return current_app.response_class(response='', status=204)

    def update_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        instance = self._fetch_object(resource, id)
        payload = self._get_json()
        self._validate_update_relationship_request(relationship, payload)
        self._check_full_replacement(relationship, source_pointer=None)
        resource.store.update(
            instance=instance,
            fields={
                relationship.name: self._parse_relationship(
                    resource=resource,
                    relationship=relationship,
                    data=payload['data'],
                    source_pointer='/data',
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
                source_pointer='/data',
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
                source_pointer='/data/relationships'
            )
        )
        return fields

    def _validate_create_request(self, resource, payload):
        schema = schemas.get_top_level_schema(resource, for_update=False)
        self._validate(payload, schema)
        data = payload['data']
        type_ = data['type']
        if type_ != resource.type:
            raise errors.TypeMismatch(type=type_, source_pointer='/data/type')
        if 'id' in data and not resource.allow_client_generated_ids:
            raise errors.ClientGeneratedIDsUnsupported(type_)

    def _validate_update_request(self, resource, id, payload):
        schema = schemas.get_top_level_schema(resource, for_update=True)
        self._validate(payload, schema)
        data = payload['data']
        if data['type'] != resource.type:
            raise errors.TypeMismatch(
                type=data['type'],
                source_pointer='/data/type'
            )
        if data['id'] != id:
            raise errors.IDMismatch(data['id'])

    def _validate_update_relationship_request(self, relationship, payload):
        schema = schemas.get_relationship_object_schema(relationship)
        self._validate(payload, schema)

    def _parse_relationships(self, resource, relationships, source_pointer):
        relationships = [
            (resource.relationships[relationship_name], value)
            for relationship_name, value in relationships.items()
        ]
        for relationship, _ in relationships:
            self._check_full_replacement(
                relationship=relationship,
                source_pointer=source_pointer + '/' + relationship.name
            )
        return {
            relationship.name: self._parse_relationship(
                resource=resource,
                relationship=relationship,
                data=value['data'],
                source_pointer=(
                    source_pointer + '/' + relationship.name + '/data'
                )
            )
            for relationship, value in relationships
        }

    def _check_full_replacement(self, relationship, source_pointer):
        if relationship.many and not relationship.allow_full_replacement:
            raise errors.FullReplacementDisallowed(
                relationship=relationship.name,
                source_pointer=source_pointer
            )

    def _parse_relationship(
        self, resource, relationship, data, source_pointer,
        ignore_not_found=False
    ):
        if relationship.many:
            return self._parse_linkages(
                relationship,
                linkages=data,
                source_pointer=source_pointer,
                ignore_not_found=ignore_not_found
            )
        else:
            return self._parse_linkage(
                relationship=relationship,
                linkage=data,
                source_pointer=source_pointer
            )

    def _parse_linkage(self, relationship, linkage, source_pointer):
        if linkage is not None:
            if linkage['type'] != relationship.type:
                raise errors.TypeMismatch(
                    type=linkage['type'],
                    source_pointer=source_pointer + '/type'
                )
            return self._fetch_object(
                resource=relationship.resource,
                id=linkage['id'],
                source_pointer=source_pointer
            )

    def _parse_linkages(
        self, relationship, linkages, source_pointer, ignore_not_found=False
    ):
        objs = []
        for i, linkage in enumerate(linkages):
            try:
                obj = self._parse_linkage(
                    relationship=relationship,
                    linkage=linkage,
                    source_pointer=source_pointer + '/' + str(i)
                )
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
            raise errors.ValidationError(
                detail=e.message,
                source_pointer='/' + '/'.join(e.path)
            )

    def _get_json(self):
        data = request.get_data()
        try:
            return json.loads(data)
        except ValueError as e:
            raise errors.InvalidJSON(detail=str(e))

    def _fetch_object(self, resource, id, params=None, source_pointer=None):
        try:
            return resource.store.fetch_one(resource.model_class, id, params)
        except exceptions.ObjectNotFound:
            raise errors.ResourceNotFound(
                type=resource.type,
                id=id,
                source_pointer=source_pointer
            )

    def _get_resource(self, type):
        try:
            return self.resource_registry.by_type[type]
        except KeyError:
            raise errors.ResourceTypeNotFound(type=type)

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

    def _serialize(self, input, params, links):
        serializer = Serializer(self.resource_registry, params)
        data = serializer.dump(input, links)
        return json.dumps(data)

    def _get_links(self, params, count=None):
        links = {
            'self': request.base_url + self._build_query_string(params.raw)
        }
        if count is not None:
            links.update(self._get_pagination_links(params, count))
        return links

    def _get_pagination_links(self, params, count):
        link_params = params.pagination.get_link_params(count)
        links = {}
        for name, page_params in link_params.items():
            if page_params:
                raw_params = params.raw.copy()
                raw_params['page'] = page_params
                link = request.base_url + self._build_query_string(raw_params)
            else:
                link = None
            links[name] = link
        return links

    def _build_query_string(self, params):
        query_string = url_encode(qstring.unnest(params))
        if query_string:
            query_string = '?' + query_string
        return query_string

    def _serialize_relationship(self, input, params, links):
        serializer = Serializer(self.resource_registry, params)
        data = serializer.dump_relationship(input, links)
        return json.dumps(data)
