import itertools

from .. import link_builder


def dump_resource_collection_links(type, params=None):
    return {
        'self': link_builder.build_resource_collection_url(type=type)
    }


def dump_individual_resource_links(type, id, params=None):
    return {
        'self': link_builder.build_individual_resource_url(type=type, id=id)
    }


def dump_related_links(type, id, relationship, params=None):
    return {
        'self': link_builder.build_related_url(
            type=type,
            id=id,
            relationship=relationship
        )
    }


def dump_relationship_links(type, id, relationship, params=None):
    return {
        'self': link_builder.build_relationship_url(
            type=type,
            id=id,
            relationship=relationship
        ),
        'related': link_builder.build_related_url(
            type=type,
            id=id,
            relationship=relationship
        ),
    }


def get_identifier(resource, model):
    return (resource.type, resource.store.get_id(model))
