import qstring
from flask import json, request
from flask.views import MethodView

from . import serialization
from .errors import InvalidJSON, JSONAPIException
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


class BaseView(MethodView):
    def parse_query_parameters(self):
        pass

    def get_json(self):
        data = request.get_data()
        try:
            return json.loads(data)
        except ValueError as e:
            raise JSONAPIException(InvalidJSON(detail=str(e)))

    def dispatch_request(self, *args, **kwargs):
        self.parse_query_parameters()
        return super(BaseView, self).dispatch_request(*args, **kwargs)


class ResourceView(BaseView):
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
        pagination = self.resource.fetch_many(
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
        model = self.resource.fetch_one(id, include=self.include)
        data = serialization.document.resource.dump(
            resource=self.resource,
            model=model,
            fields=self.fields,
            include=self.include
        )
        return json.dumps(data)

    def delete(self, id):
        self.resource.delete(id)
        return '', 204


class RelatedView(BaseView):
    def __init__(self, relationship):
        self.relationship = relationship

    def parse_query_parameters(self):
        params = qstring.nest(request.args.items(multi=True))
        self.fields = parse_fields_parameter(
            resource_registry=self.relationship.resource._registry,
            value=params.get('fields')
        )
        self.include = parse_include_parameter(
            resource=self.relationship.resource,
            value=params.get('include')
        )
        self.page = parse_page_parameter(
            resource=self.relationship.resource,
            value=params.get('page')
        )

    def get(self, id):
        model = self.relationship.parent.fetch_one(id)
        if self.relationship.many:
            pagination = self.relationship.parent.store.fetch_many_related(
                model=model,
                relationship=self.relationship.name,
                page=self.page
            )
            data = serialization.document.resource_collection.dump(
                resource=self.relationship.resource,
                models=pagination.models,
                fields=self.fields,
                include=self.include
            )
        else:
            related = self.relationship.parent.store.fetch_one_related(
                model=model,
                relationship=self.relationship.name,
            )
            data = serialization.document.resource.dump(
                resource=self.relationship.resource,
                model=related,
                fields=self.fields,
                include=self.include
            )
        return json.dumps(data)


class ToManyRelationshipView(BaseView):
    def __init__(self, relationship):
        self.relationship = relationship

    def parse_query_parameters(self):
        params = qstring.nest(request.args.items(multi=True))
        self.page = parse_page_parameter(
            resource=self.relationship.resource,
            value=params.get('page')
        )

    def get(self, id):
        model = self.relationship.parent.fetch_one(id)
        pagination = self.relationship.parent.store.fetch_many_related(
            model=model,
            relationship=self.relationship.name,
            page=self.page
        )
        data = serialization.document.relationship.dump(
            relationship=self.relationship,
            related=pagination.models,
        )
        return json.dumps(data)

    def post(self, id):
        model = self.relationship.parent.fetch_one(id)
        self.relationship.parent.store.create_relationship(
            model=model,
            relationship=self.relationship.name,
            values=serialization.document.relationship.load(
                relationship=self.relationship,
                raw_data=self.get_json()
            )
        )
        return '', 204

    def patch(self, id):
        model = self.relationship.parent.fetch_one(id)
        self.relationship.parent.store.update(model=model, fields={
            self.relationship.name: serialization.document.relationship.load(
                relationship=self.relationship,
                raw_data=self.get_json(),
                replace=True
            )
        })
        return '', 204

    def delete(self, id):
        model = self.relationship.parent.fetch_one(id)
        self.relationship.parent.store.delete_relationship(
            model=model,
            relationship=self.relationship.name,
            values=serialization.document.relationship.load(
                relationship=self.relationship,
                raw_data=self.get_json()
            )
        )
        return '', 204


class ToOneRelationshipView(BaseView):
    def __init__(self, relationship):
        self.relationship = relationship

    def get(self, id):
        model = self.relationship.parent.fetch_one(id)
        related = self.relationship.parent.store.fetch_one_related(
            model=model,
            relationship=self.relationship.name,
        )
        data = serialization.document.relationship.dump(
            relationship=self.relationship,
            related=related,
        )
        return json.dumps(data)

    def patch(self, id):
        model = self.relationship.parent.fetch_one(id)
        self.relationship.parent.store.update(model=model, fields={
            self.relationship.name: serialization.document.relationship.load(
                relationship=self.relationship,
                raw_data=self.get_json()
            )
        })
        return '', 204
