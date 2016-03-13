from . import link_builder, resource_linkage


def dump(relationship, model):
    data = {
        'links': {
            'self': link_builder.relationship_self_link(
                relationship=relationship,
                model=model
            ),
            'related': link_builder.relationship_related_link(
                relationship=relationship,
                model=model
            )
        }
    }
    if relationship.allow_include:
        data['data'] = resource_linkage.dump(
            relationship=relationship,
            related=getattr(model, relationship.name),
        )
    return data
