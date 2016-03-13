from flask import url_for

from . import resource_identifier


def resource_self_link(resource, model):
    data = resource_identifier.dump(resource=resource, model=model)
    return url_for('jsonapi.fetch_one', **data, _external=True)


def relationship_self_link(relationship, model):
    data = resource_identifier.dump(resource=relationship.parent, model=model)
    return url_for(
        'jsonapi.fetch_relationship',
        **data,
        relationship=relationship.name,
        _external=True
    )


def relationship_related_link(relationship, model):
    data = resource_identifier.dump(resource=relationship.parent, model=model)
    return url_for(
        'jsonapi.fetch_related',
        **data,
        relationship=relationship.name,
        _external=True
    )
