import functools
import json

from . import _parsers, relationship_object


def dump(resource, model, fields=None):
    relationships = _get_included_relationships(
        resource=resource,
        fields=fields
    )
    return {
        relationship_name: relationship_object.dump(
            relationship=resource.relationships[relationship_name],
            model=model
        )
        for relationship_name in relationships
    }


def _get_included_relationships(resource, fields):
    if fields is None:
        return set(resource.relationships)
    return fields & set(resource.relationships)


def load(resource, raw_data):
    parser = _RelationshipsObject(resource)
    return parser(raw_data)


class _RelationshipsObject(_parsers.Object):
    def __init__(self, resource):
        super(_RelationshipsObject, self).__init__(
            properties={
                relationship.name: functools.partial(
                    relationship_object.load,
                    relationship,
                    replace=True
                )
                for relationship in resource.relationships.values()
            },
            additional_properties=False
        )
        self.resource = resource

    def _build_additional_properties_message(self, extra):
        msg = '{extra} {rest}'.format(
            extra=self._build_property_list_message(extra),
            rest=(
                'is not a valid relationship' if len(extra) == 1
                else 'are not valid relationships'
            )
        )
        return msg + ' for {type} resource'.format(
            type=json.dumps(self.resource.type)
        )
