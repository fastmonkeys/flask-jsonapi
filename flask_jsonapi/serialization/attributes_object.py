import json

from . import _parsers


def dump(resource, model, fields=None):
    attributes = _get_included_attributes(resource=resource, fields=fields)
    data = {attr: getattr(model, attr) for attr in attributes}
    return resource.serialize_attributes(data)


def _get_included_attributes(resource, fields):
    if fields is None:
        return set(resource.attributes)
    return fields & set(resource.attributes)


def load(resource, raw_data):
    parser = _AttributesObject(resource)
    return parser(raw_data)


class _AttributesObject(_parsers.Object):
    def __init__(self, resource):
        super(_AttributesObject, self).__init__(
            properties={
                attribute.name: _parsers.Any()
                for attribute in resource.attributes.values()
            },
            additional_properties=False
        )
        self.resource = resource

    def __call__(self, raw_data):
        data = super(_AttributesObject, self).__call__(raw_data)
        return self.resource.deserialize_attributes(data)

    def _build_additional_properties_message(self, extra):
        msg = '{extra} {rest}'.format(
            extra=self._build_property_list_message(extra),
            rest=(
                'is not a valid attribute' if len(extra) == 1
                else 'are not valid attributes'
            )
        )
        return msg + ' for {type} resource'.format(
            type=json.dumps(self.resource.type)
        )
