import json

from . import _parsers
from ..errors import (
    JSONAPIException,
    ResourceNotFound,
    TypeMismatch,
    ValidationError
)
from ..exceptions import ObjectNotFound


def dump(resource, model):
    return {
        'type': resource.type,
        'id': str(getattr(model, 'id'))
    }


def load(resource, data):
    parser = _ResourceIdentifier(resource)
    return parser(data)


class _ResourceIdentifier(_parsers.Object):
    def __init__(self, resource):
        self.resource = resource
        super(_ResourceIdentifier, self).__init__(
            properties={
                'type': _ResourceType(resource),
                'id': _ResourceId(resource),
            },
            required=['type', 'id']
        )

    def __call__(self, raw_data):
        data = super(_ResourceIdentifier, self).__call__(raw_data)
        try:
            return self.resource.store.fetch_one(id=data['id'])
        except ObjectNotFound:
            error = ResourceNotFound(
                type=self.resource.type,
                id=raw_data['id'],
                source_path=[]
            )
            raise JSONAPIException(error)


class _ResourceType(_parsers.String):
    def __init__(self, resource):
        self.resource = resource

    def __call__(self, raw_data):
        super(_ResourceType, self).__call__(raw_data)
        if raw_data != self.resource.type:
            error = TypeMismatch(
                actual_type=raw_data,
                expected_type=self.resource.type,
                source_path=[]
            )
            raise JSONAPIException(error)
        return raw_data


class _ResourceId(_parsers.String):
    def __init__(self, resource):
        self.resource = resource

    def __call__(self, raw_data):
        super(_ResourceId, self).__call__(raw_data)
        try:
            return self.resource.id_deserializer(raw_data)
        except ValueError:
            detail = '{value} is not a valid {type}'.format(
                value=json.dumps(raw_data),
                type=self.resource.id_deserializer.__name__
            )
            error = ValidationError(detail=detail, source_path=[])
            raise JSONAPIException(error)
