from collections import OrderedDict

from .datastructures import Page
from .errors import (
    InvalidField,
    InvalidFieldsFormat,
    InvalidFieldsValueFormat,
    InvalidInclude,
    InvalidIncludeFormat,
    InvalidPageFormat,
    InvalidPageParameter,
    InvalidPageValue,
    InvalidResourceType,
    JSONAPIException
)


def parse_fields_parameter(resource_registry, value):
    if value is None:
        value = {}

    fields = {}

    try:
        field_items = value.items()
    except AttributeError:
        raise JSONAPIException(InvalidFieldsFormat())

    for type, field_names in field_items:
        try:
            resource = resource_registry.by_type[type]
        except KeyError:
            raise JSONAPIException(InvalidResourceType(type=type))

        try:
            field_names = field_names.split(',')
        except AttributeError:
            raise JSONAPIException(InvalidFieldsValueFormat(type=type))

        for field_name in field_names:
            if field_name not in resource.fields:
                raise JSONAPIException(
                    InvalidField(type=resource.type, field=field_name)
                )

        fields[type] = set(field_names)

    return fields


def parse_page_parameter(resource, value):
    if value is None:
        value = {}

    _validate_page_params(value)

    return Page(
        number=_parse_page_number(value),
        size=_parse_page_size(resource, value)
    )


def _validate_page_params(value):
    try:
        keys = value.keys()
    except AttributeError:
        raise JSONAPIException(InvalidPageFormat())

    for key in keys:
        if key not in {'number', 'size'}:
            raise JSONAPIException(InvalidPageParameter(param=key))


def _parse_page_number(value):
    try:
        number = int(value.get('number', 1))
    except ValueError:
        raise JSONAPIException(InvalidPageValue(param='number'))

    if number < 1:
        raise JSONAPIException(InvalidPageValue(param='number'))

    return number


def _parse_page_size(resource, value):
    try:
        size = int(value.get('size', resource.default_page_size))
    except ValueError:
        raise JSONAPIException(InvalidPageValue(param='size'))

    if size < 1:
        raise JSONAPIException(InvalidPageValue(param='size'))

    if size > resource.max_page_size:
        detail = 'Page size exceeds the maximum page size of {max_page_size}'
        detail = detail.format(max_page_size=resource.max_page_size)
        raise JSONAPIException(InvalidPageValue(detail=detail, param='size'))

    return size


def parse_include_parameter(resource, value):
    if value is None:
        value = ''

    root = OrderedDict()

    if value == '':
        return root

    try:
        relationship_paths = value.split(',')
    except AttributeError:
        raise JSONAPIException(InvalidIncludeFormat())

    for relationship_path in relationship_paths:
        current_node = root
        current_resource = resource
        for relationship_name in relationship_path.split('.'):
            relationships = current_resource.relationships
            try:
                relationship = relationships[relationship_name]
            except KeyError:
                raise JSONAPIException(InvalidInclude(
                    type=current_resource.type,
                    relationship=relationship_name
                ))
            current_resource = relationship.resource
            current_node.setdefault(relationship_name, OrderedDict())
            current_node = current_node[relationship_name]

    return root
