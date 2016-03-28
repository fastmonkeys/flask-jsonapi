import qstring
from flask import json, request
from flask.views import MethodView

from . import serialization
from .errors import JSONAPIException, ResourceNotFound
from .exceptions import ObjectNotFound
from .params import (
    parse_fields_parameter,
    parse_include_parameter,
    parse_page_parameter
)


# @blueprint.after_request
# def set_response_content_type(response):
#     response.mimetype = 'application/vnd.api+json'
#     return response
#


class ResourceView(MethodView):
    def __init__(self, resource):
        self.resource = resource

    def parse_query_parameters(self):
        params = qstring.nest(request.args.items(multi=True))
        self.fields = parse_fields_parameter(
            resource_registry=self.resource._registry,
            value=params.get('fields')
        )
        self.include = parse_include_parameter(
            resource=self.resource,
            value=params.get('include')
        )
        self.page = parse_page_parameter(
            resource=self.resource,
            value=params.get('page')
        )

    def get(self, id):
        if id is None:
            return self.get_many()
        else:
            return self.get_one(id)

    def get_many(self):
        pagination = self.resource.store.fetch_many(
            include=self.include,
            page=self.page
        )
        data = serialization.document.resource_collection.dump(
            resource=self.resource,
            models=pagination.models,
            fields=self.fields,
            include=self.include
        )
        return json.dumps(data)

    def get_one(self, id):
        try:
            model = self.resource.store.fetch_one(id, include=self.include)
        except ObjectNotFound:
            raise JSONAPIException(ResourceNotFound(
                type=self.resource.type,
                id=id
            ))
        data = serialization.document.resource.dump(
            resource=self.resource,
            model=model,
            fields=self.fields,
            include=self.include
        )
        return json.dumps(data)

    def delete(self, id):
        try:
            model = self.resource.store.fetch_one(id)
        except ObjectNotFound:
            pass
        else:
            self.resource.store.delete(model)
        return '', 204

    def dispatch_request(self, *args, **kwargs):
        self.parse_query_parameters()
        return super(ResourceView, self).dispatch_request(*args, **kwargs)


class RelatedView(MethodView):
    pass


class RelationshipView(MethodView):
    pass
