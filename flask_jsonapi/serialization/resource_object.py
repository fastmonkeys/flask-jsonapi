from . import (
    _parsers,
    attributes_object,
    link_builder,
    relationships_object,
    resource_identifier
)


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


def load(resource, raw_data):
    parser = _parsers.Object(
        properties={
            'type': resource_identifier._ResourceType(resource)
        },
        required=['type']
    )
    parser(raw_data)
