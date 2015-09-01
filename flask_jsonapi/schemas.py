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
    else:
        if any(resource.required_attributes):
            required.append('attributes')
        if any(resource.required_relationships):
            required.append('relationships')
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
    required = [a.name for a in resource.required_attributes]
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
    required = [r.name for r in resource.required_relationships]
    if not for_update and required:
        schema['required'] = required
    return schema


def get_relationship_object_schema(relationship):
    if relationship.many:
        definition = {
            'type': 'array',
            'items': get_resource_identifier_object_schema()
        }
    else:
        definition = get_resource_identifier_object_schema(allow_null=True)
    return {
        'type': 'object',
        'required': ['data'],
        'properties': {
            'data': definition
        }
    }


def get_resource_identifier_object_schema(allow_null=False):
    type_ = ['object']
    if allow_null:
        type_.append('null')
    return {
        'type': type_,
        'required': [
            'type',
            'id'
        ],
        'properties': {
            'type': {'type': 'string'},
            'id': {'type': 'string'}
        }
    }
