from collections import defaultdict

from flask import url_for


def get_collection_url(query_params): #find_link
    return url_for('jsonapi.get', type='...', **query_params)

def get_individual_resource_url(): # self_href
    return url_for('jsonapi.get', type='...', id='...')


class ResourceObject(object):
    def __init__(self, resources, model, params):
        self.resources = resources
        self.model = model
        self.resource = self.resources.by_model_class[model.__class__]
        self.params = params

    @property
    def data(self):
        resource_object = {
            "id": model.id,
            "type": resource.type,
        }

        attributes_object = self.attributes
        if attributes_object:
            resource_object["attributes"] = attributes_object

        relationships_object = self.relationships
        if relationships_object:
            resource_object["relationships"] = relationships_object

        links_object = self._dump_links_object(resource)
        if links_object:
            resource_object["links"] = links_object

        return resource_object

    @property
    def attributes(self):
        attributes = self.params.fields[self.resource.type] & self.resource.attributes
        return {
            attr: self.resource.repository.get_attribute(attr)
            for attr in attributes
        }

    @property
    def relationships(self):
        relationships = self.params.fields[self.resource.type] & self.resource.relationships
        return {
            relationship: RelationshipObject().dump(model, relationship)
            for relationship in relationships
        }

    def _build_relationship_object(self, relationship):


class RelationshipObjectSerializer(object):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    @property
    def data(self   ):
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
