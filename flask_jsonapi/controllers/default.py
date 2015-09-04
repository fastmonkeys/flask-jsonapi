import qstring
from flask import abort, current_app, json, request
from werkzeug.urls import url_encode

from .. import errors, exceptions, link_builder
from ..params import Parameters
from ..request_parser import RequestParser
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
        parser = RequestParser(resource=resource)
        result = parser.parse(data=self._get_json())
        try:
            instance = resource.store.create(
                model_class=resource.model_class,
                id=result.id,
                fields=result.fields
            )
        except exceptions.ObjectAlreadyExists:
            raise errors.ResourceAlreadyExists(type=type, id=result.id)
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
        parser = RequestParser(resource=resource, id=id)
        result = parser.parse(data=self._get_json())
        resource.store.update(instance=instance, fields=result.fields)
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
        parser = RequestParser(resource=resource, id=id)
        resource.store.create_relationship(
            instance=instance,
            relationship=relationship.name,
            values=parser.parse_relationship_object(
                relationship=relationship,
                data=self._get_json(),
                path=[]
            )
        )
        return current_app.response_class(response='', status=204)

    def update_relationship(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        instance = self._fetch_object(resource, id)
        parser = RequestParser(resource=resource, id=id)
        resource.store.update(
            instance=instance,
            fields={
                relationship.name: parser.parse_relationship_object(
                    relationship=relationship,
                    data=self._get_json(),
                    path=[],
                    check_full_replacement=True
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
        parser = RequestParser(resource=resource, id=id)
        resource.store.delete_relationship(
            instance=instance,
            relationship=relationship.name,
            values=parser.parse_relationship_object(
                relationship=relationship,
                data=self._get_json(),
                path=[],
                ignore_not_found=True
            )
        )
        return current_app.response_class(response='', status=204)

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
