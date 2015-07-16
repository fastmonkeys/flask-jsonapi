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


class ResourceSerializer(object):
    def __init__(self, resource_registry, fields=None, include=None):
        self.resource_registry = resource_registry
        self.fields = fields or {}
        self.include = include or []

    def dump(self, resources):
        is_collection = isinstance(resources, list)
        self.resource_objects = defaultdict(dict)
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

    def _process_primary_resource(self, resource):
        self._add_resource_object
        self._make_primary(type=resource._meta.type, id=resource._model.id)


    def _has_been_serialized(self, type, id):
        return (
            type in self.resource_objects and
            id in self.resource_objects[type]
        )

    def _dump_resource_object(self, resource):
        resource_object = {
            "id": resource.model.id,
            "type": resource._meta.type,
        }

        attributes_object = self._dump_attributes_object(resource)
        if attributes_object:
            resource_object["attributes"] = attributes_object

        relationships_object = self._dump_relationships_object(resource)
        if relationships_object:
            resource_object["relationships"] = relationships_object

        links_object = self._dump_links_object(resource)
        if links_object:
            resource_object["links"] = links_object

        return resource_object

    def _dump_attributes_object(self, resource):
        return {
            name: getattr(resource.model, name)
            for name in resource._meta.attributes
        }

    def _dump_relationships_object(self, resource):
        relationships = resource._meta.relationships
        for name in relationships:
            relationship_property = getattr(resource._meta.model_class, name)
            if relationship_property.uselist:
                related_resources = getattr(resource.model, name)
                for related_resource in related_resources:

            else:
                related_resource = getattr(resource.model, name)

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

    def _dump_links_object_for_has_one_relationship(self, resource, relationship):
      link_object_hash = {}
      link_object_hash[:links] = {}
      link_object_hash[:links][:self] = self_link(source, association)
      link_object_hash[:links][:related] = related_link(source, association)
      link_object_hash[:data] = has_one_linkage(source, association)
      link_object_hash

    def link_object_has_many(source, association, include_linkage)
      link_object_hash = {}
      link_object_hash[:links] = {}
      link_object_hash[:links][:self] = self_link(source, association)
      link_object_hash[:links][:related] = related_link(source, association)
      link_object_hash[:data] = has_many_linkage(source, association) if include_linkage
      link_object_hash
    end

    def self_link(source, association)
      "#{self_href(source)}/relationships/#{format_route(association.name)}"
    end

    def related_link(source, association)
      "#{self_href(source)}/#{format_route(association.name)}"
    end

    def has_one_linkage(source, association)
      linkage = {}
      linkage_id = foreign_key_value(source, association)
      if linkage_id
        linkage[:type] = format_key(association.type)
        linkage[:id] = linkage_id
      else
        linkage = nil
      end
      linkage
    end

    def has_many_linkage(source, association)
      linkage = []
      linkage_ids = foreign_key_value(source, association)
      linkage_ids.each do |linkage_id|
        linkage.append({type: format_key(association.type), id: linkage_id})
      end
      linkage
    end
