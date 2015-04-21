from flask import url_for
from marshmallow.fields import *


class Link(Field):
    pass


class Related(Link):
    def __init__(self, related_schema, many=False, as_object=True, **kwargs):
        self.related_schema = related_schema
        self.many = many
        self.as_object = as_object
        super(Related, self).__init__(**kwargs)

    def get_value(self, key, obj, accessor=None):
        value = super(Related, self).get_value(key, obj, accessor)
        related = url_for(
            'jsonapi.get_related',
            type=self.parent.opts.type,
            id=obj.id,
            relationship=key
        )
        if self.as_object:
            if self.many:
                linkage = [make_linkage_object(self.related_schema, v) for v in value]
            else:
                linkage = make_linkage_object(self.related_schema, value)
            return {
                'linkage': linkage,
                'related': related,
                'self': url_for(
                    'jsonapi.get_relationship',
                    type=self.parent.opts.type,
                    id=obj.id,
                    relationship=key
                )
            }
        else:
            return related


def make_linkage_object(schema_cls, obj):
    if obj is not None:
        schema = schema_cls(only=('id', 'type'))
        result = schema.dump(obj)
        return result.data


class Self(Link):
    def get_value(self, key, obj, accessor=None):
        return url_for(
            'jsonapi.get',
            type=self.parent.opts.type,
            id=obj.id,
        )
