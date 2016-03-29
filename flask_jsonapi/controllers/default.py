import qstring
from flask import abort, current_app, json, request
from werkzeug.urls import url_encode

from .. import errors, exceptions, serialization
from ..request_parser import RequestParser


class DefaultController(object):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    def create(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        parser = RequestParser(resource=resource)
        result = parser.parse(data=self._get_json())

        ###
        try:
            instance = resource.store.create(
                model_class=resource.model_class,
                id=result.id,
                fields=result.fields
            )
        except exceptions.ObjectAlreadyExists:
            raise errors.ResourceAlreadyExists(type=type, id=result.id)

        links = serializer.dump_individual_resource_links(
            type=type,
            id=resource.store.get_id(instance)
        )
        data = serializer.dump_document(
            resource_registry=self.resource_registry,
            params=params,
            input=instance,
            links=links
        )

        return current_app.response_class(
            response=json.dumps(data),
            status=201,
            headers={'Location': links['self']}
        )

    def update(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)

        ###
        instance = self._fetch_object(resource, id)
        parser = RequestParser(resource=resource, id=id)
        result = parser.parse(data=self._get_json())
        resource.store.update(instance=instance, fields=result.fields)
        links = self._get_links(params)
        return self._serialize(instance, params, links)

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
