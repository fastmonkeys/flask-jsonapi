from . import attributes_object, relationships_object, resource_identifier


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

    # TODO:
    # data['links'] = dump_individual_resource_links(
    #     type=data['type'],
    #     id=data['id']
    # )

    return data
