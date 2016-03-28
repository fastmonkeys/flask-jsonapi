import qstring
from flask import json, request
from flask.views import MethodView

from . import serialization
from .errors import JSONAPIException, ResourceNotFound
from .exceptions import ObjectNotFound
from .params import parse_fields_parameter, parse_include_parameter


# @blueprint.after_request
# def set_response_content_type(response):
#     response.mimetype = 'application/vnd.api+json'
#     return response
#


class ResourceView(MethodView):
    def __init__(self, resource):
        self.resource = resource

    def get(self, id):
        params = qstring.nest(request.args.items(multi=True))
        fields = parse_fields_parameter(
            resource_registry=self.resource._registry,
            value=params.get('fields')
        )
        include = parse_include_parameter(
            resource=self.resource,
            value=params.get('include')
        )
        try:
            model = self.resource.store.fetch_one(id, include=include)
        except ObjectNotFound:
            raise JSONAPIException(ResourceNotFound(type=self.resource.type, id=id))
        data = serialization.document.resource.dump(
            resource=self.resource,
            model=model,
            fields=fields,
            include=include
        )
        return json.dumps(data)


class RelatedView(MethodView):
    pass


class RelationshipView(MethodView):
    pass
