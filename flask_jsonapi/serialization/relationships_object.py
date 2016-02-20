from . import relationship_object


def dump(resource, model, fields=None):
    relationships = _get_included_relationships(
        resource=resource,
        fields=fields
    )
    return {
        relationship_name: relationship_object.dump(
            relationship=resource.relationships[relationship_name],
            model=model
        )
        for relationship_name in relationships
    }


def _get_included_relationships(resource, fields):
    if fields is None:
        return set(resource.relationships)
    return fields & set(resource.relationships)
