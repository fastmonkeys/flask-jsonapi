def get_top_level_schema(resource, for_update):
    return {
        'type': 'object',
        'required': ['data'],
        'properties': {
            'data': get_resource_object_schema(resource, for_update)
        }
    }


def get_resource_object_schema(resource, for_update):
    required = ['type']
    if for_update:
        required.append('id')
    return {
        'type': 'object',
        'required': required,
        'properties': {
            'type': {'type': 'string'},
            'id': {'type': 'string'},
            'attributes': get_attributes_object_schema(resource, for_update),
            'relationships': get_relationships_object_schema(
                resource,
                for_update
            )
        }
    }


def get_attributes_object_schema(resource, for_update):
    schema = {
        'type': 'object',
        'properties': {
            attribute: {}
            for attribute in resource.attributes
        },
        'additionalProperties': False
    }
    required = [
        attribute.name
        for attribute in resource.attributes.values()
        if attribute.required
    ]
    if not for_update and required:
        schema['required'] = required
    return schema


def get_relationships_object_schema(resource, for_update):
    schema = {
        'type': 'object',
        'properties': {
            relationship.name: get_relationship_object_schema(relationship)
            for relationship in resource.relationships.values()
        },
        'additionalProperties': False
    }
    required = [
        relationship.name
        for relationship in resource.relationships.values()
        if relationship.required
    ]
    if not for_update and required:
        schema['required'] = required
    return schema


def get_relationship_object_schema(relationship):
    if relationship.many:
        definition = {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': [
                    'type',
                    'id'
                ],
                'properties': {
                    'type': {'type': 'string'},
                    'id': {'type': 'string'}
                }
            }
        }
    else:
        definition = {
            'type': ['null', 'object'],
            'required': [
                'type',
                'id'
            ],
            'properties': {
                'type': {'type': 'string'},
                'id': {'type': 'string'}
            }
        }
    return {
        'type': 'object',
        'required': ['data'],
        'properties': {
            'data': definition
        }
    }
