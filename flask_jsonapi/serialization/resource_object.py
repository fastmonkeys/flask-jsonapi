from . import attributes_object, relationships_object, resource_identifier, link_builder


def dump(resource, model, fields):
    data = resource_identifier.dump(resource=resource, model=model)

    attributes = attributes_object.dump(
        resource=resource,
        model=model,
        fields=fields
    )
    if attributes:
        data['attributes'] = attributes

    relationships = relationships_object.dump(
        resource=resource,
        model=model,
        fields=fields
    )
    if relationships:
        data['relationships'] = relationships

    data['links'] = {
        'self': link_builder.resource_self_link(
            resource=resource,
            model=model
        )
    }

    return data
