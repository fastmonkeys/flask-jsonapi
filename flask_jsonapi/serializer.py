from collections import defaultdict

from flask import url_for


def get_collection_url(query_params): #find_link
    return url_for('jsonapi.get', type='...', **query_params)

def get_individual_resource_url(): # self_href
    return url_for('jsonapi.get', type='...', id='...')

def get_relationship_url():   # self_link
    return url_for('jsonapi.get_relationship', type='..', id='...', relationship='...')

def get_related_resource_url():  # related_link
    return url_for('jsonapi.get_related', type='..', id='...', relationship='...')

#
# {                                                                             // Top Level
#   "links": {                                                                  // A Links Object related to the primary data.
#     "self": "http://example.com/posts",
#     "next": "http://example.com/posts?page[offset]=2",
#     "last": "http://example.com/posts?page[offset]=10"
#   },
#   "data": [{                                                                  // The document's "primary data"
#     "type": "posts",
#     "id": "1",
#     "attributes": {
#       "title": "JSON API paints my bikeshed!"
#     },
#     "relationships": {
#       "author": {
#         "links": {
#           "self": "http://example.com/posts/1/relationships/author",
#           "related": "http://example.com/posts/1/author"
#         },
#         "data": { "type": "people", "id": "9" }
#       },
#       "comments": {
#         "links": {
#           "self": "http://example.com/posts/1/relationships/comments",
#           "related": "http://example.com/posts/1/comments"
#         },
#         "data": [
#           { "type": "comments", "id": "5" },
#           { "type": "comments", "id": "12" }
#         ]
#       }
#     },
#     "links": {
#       "self": "http://example.com/posts/1"
#     }
#   }],
#   "included": [{                                                              // Included resources
#     "type": "people",
#     "id": "9",
#     "attributes": {
#       "first-name": "Dan",
#       "last-name": "Gebhardt",
#       "twitter": "dgeb"
#     },
#     "links": {
#       "self": "http://example.com/people/9"
#     }
#   }, {
#     "type": "comments",
#     "id": "5",
#     "attributes": {
#       "body": "First!"
#     },
#     "links": {
#       "self": "http://example.com/comments/5"
#     }
#   }, {
#     "type": "comments",
#     "id": "12",
#     "attributes": {
#       "body": "I like XML better"
#     },
#     "links": {
#       "self": "http://example.com/comments/12"
#     }
#   }]
# }

class ResourceIdentifier(object):
    def dump(self, model):
        resource = self.resources.find_by_model(model)
        return {
            "id": resource.repository.get_id(model),
            "type": resource.type,
        }


class AttributesObject(object):
    def dump(self, model):
        resource = self.resources.find_by_model(model)
        attributes = resource.attributes
        requested = self.fields.get(resource.type)
        if requested is not None:
            attributes = attributes & requested
        return {
            attr: resource.repository.get_attribute(attr)
            for attr in attributes
        }


class RelationshipsObject(object):
    def dump(self, model):
        resource = self.resources.find_by_model(model)
        relationships = resource.relationships
        requested = self.fields.get(resource.type)
        if requested is not None:
            relationships = relationships & requested
        return {
            relationship: RelationshipObject().dump(model, relationship)
            for relationship in relationships
        }


class RelationshipObject(object):
    def __init__(self, resource, model, relationship):
        self.resource = resource
        self.model = model
        self.relationship = relationship

    @property
    def data(self):
        related = self.resource.repository.get_related(self.model, self.relationship)
        if self.resource.repository.is_to_many_relationship(self.model, self.relationship):
            return [
                ResourceIdentifier(self.resource, model).dump()
                for model in related
            ]
        else:
            return ResourceIdentifier(self.resource, related).dump()

    @property
    def links(self):
        return {
            "self": self.self_link,
            "related": self.related_link
        }

    @property
    def self_link(self):
        return url_for(
            'jsonapi.get_relationship',
            type=self.resource.type,
            id=self.resource.repository.get_id(self.model),
            relationship=self.relationship
        )

    @property
    def related_link(self):
        return url_for(
            'jsonapi.get_related',
            type=self.resource.type,
            id=self.resource.repository.get_id(self.model),
            relationship=self.relationship
        )

    def dump(self):
        return {
            "links": self.links,
            "data": self.data
        }


class ResourceObject(object):
    def __init__(self, resources):
        self.resources = resources

    def dump(self, model):
        resource = self.resources.find_by_model(model)
        resource_object = ResourceIdentifier(self.resources).dump(model)

        attributes_object = AttributesObject(self.resources).dump(model)
        if attributes_object:
            resource_object["attributes"] = attributes_object

        relationships_object = RelationshipsObject(resource).dump(model)
        if relationships_object:
            resource_object["relationships"] = relationships_object

        links_object = self._dump_links_object(resource)
        if links_object:
            resource_object["links"] = links_object

        return resource_object





class Document(object):
    def __init__(self, resources, fields=None, include=None):
        self.resources = resources
        self.fields = fields or {}
        self.include = include or []

    def dump(self, input):
        is_collection = isinstance(resources, list)
        self.included_resource_objects = set()
        primary_objects = []
        included_objects = []
        for objects in self.resource_objects.values():
            for obj in objects.values():
                if obj['primary']:
                    primary_objects.append(obj['data'])
                else:
                    included_objects.append(obj['data'])

        document = {}
        document['data'] = primary_objects if is_collection else primary_objects[0]
        if included_objects:
            document['included'] = included_objects

    def _process_primary_resources(self, resources):
        if isinstance(resources, list):
            for resource in resources:
                self._process_primary_resource(resource)
        elif resources is not None:
            self._process_primary_resource(resources)

    def _has_been_serialized(self, type, id):
        return (type, id) in self.included_resource_objects

    def _dump_links_object(self, resource):
        return {
            "self": url_for(
                'jsonapi.get',
                type=resource._meta.type,
                id=resource.model.id
            )
        }

    def _dump_links_object_for_relationship(self, resource, relationship):
        relationship_property = getattr(resource._meta.model_class, name)
        if relationship_property.uselist:
            pass
        else:
            pass

    def iter_included_models(self, model, include):
        resource = self.resources._by_model_class[model.__class__]
        repository = resource.repository
        for relationship in include:
            if repository.is_to_many_relationship(model, relationship):
                related_models = repository.get_related(model, relationship)
                for related_model in related_models:
                    yield related_model
                    for m in self.iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m
            else:
                related_model = repository.get_related(model, relationship)
                if related_model is not None:
                    yield related_model
                    for m in self.iter_included_models(
                        related_model,
                        include[relationship]
                    ):
                        yield m
