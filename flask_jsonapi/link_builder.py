from flask import url_for


def build_resource_collection_url(type):
    return url_for('jsonapi.fetch', type=type, _external=True)


def build_individual_resource_url(type, id):
    return url_for(
        'jsonapi.fetch_one',
        type=type,
        id=id,
        _external=True
    )


def build_related_url(type, id, relationship):
    return url_for(
        'jsonapi.fetch_related',
        type=type,
        id=id,
        relationship=relationship,
        _external=True
    )


def build_relationship_url(type, id, relationship):
    return url_for(
        'jsonapi.fetch_relationship',
        type=type,
        id=id,
        relationship=relationship,
        _external=True
    )
