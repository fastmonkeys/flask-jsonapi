def get_update_request_schema(resource):
    schema = get_create_request_schema(resource)
    schema['definitions']['resource']['required'].append('id')
    return schema


def get_update_relationship_request_schema(relationship):
    return _get_relationship_definition(relationship)


def get_create_request_schema(resource):
    return {
        "definitions": {
            "resource": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string"},
                    "id": {"type": "string"},
                    "attributes": {"$ref": "#/definitions/attributes"},
                    "relationships": {"$ref": "#/definitions/relationships"}
                }
            },
            "attributes": _get_attributes_definition(resource),
            "relationships": _get_relationships_definition(resource)
        },
        "type": "object",
        "required": ["data"],
        "properties": {
            "data": {"$ref": "#/definitions/resource"}
        }
    }


def _get_attributes_definition(resource):
    return {
        "type": "object",
        "properties": {
            attribute: {}
            for attribute in resource.attributes
        },
        "additionalProperties": False
    }


def _get_relationships_definition(resource):
    return {
        "type": "object",
        "properties": {
            relationship.name: _get_relationship_definition(relationship)
            for relationship in resource.relationships.values()
        },
        "additionalProperties": False
    }


def _get_relationship_definition(relationship):
    if relationship.many:
        definition = {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "type",
                    "id"
                ],
                "properties": {
                    "type": {"type": "string"},
                    "id": {"type": "string"}
                }
            }
        }
    else:
        definition = {
            "type": ["null", "object"],
            "required": [
                "type",
                "id"
            ],
            "properties": {
                "type": {"type": "string"},
                "id": {"type": "string"}
            }
        }
    return {
        "type": "object",
        "required": ["data"],
        "properties": {
            "data": definition
        }
    }
