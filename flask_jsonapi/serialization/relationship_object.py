from . import _parsers, link_builder, resource_linkage


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


def load(relationship, raw_data):
    parser = _parsers.Object(
        properties={
            'data': lambda raw_data: resource_linkage.load(
                relationship=relationship,
                raw_data=raw_data
            )
        },
        required=['data']
    )
    return parser(raw_data)['data']
