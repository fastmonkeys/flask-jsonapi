from flask import url_for

from . import resource_identifier


def resource_self_link(resource, model):
    return url_for(
        '{}.resource'.format(resource.type),
        id=model.id,
        _external=True
    )


def relationship_self_link(relationship, model):
    return url_for(
        '{type}.relationship_{relationship}'.format(
            type=relationship.parent.type,
            relationship=relationship.name
        ),
        id=model.id,
        _external=True
    )


def relationship_related_link(relationship, model):
    return url_for(
        '{type}.related_{relationship}'.format(
            type=relationship.parent.type,
            relationship=relationship.name
        ),
        id=model.id,
        _external=True
    )
