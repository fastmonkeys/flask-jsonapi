from . import resource_linkage


def dump(relationship, model):
    data = {
        'links': {}
    }
    if relationship.allow_include:
        data['data'] = resource_linkage.dump(
            relationship=relationship,
            related=getattr(model, relationship.name),
        )
    return data
