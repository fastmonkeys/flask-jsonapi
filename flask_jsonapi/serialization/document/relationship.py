from .. import relationship_object, resource_linkage
from .base import _BaseSerializer


def dump(*args, **kwargs):
    return _RelationshipSerializer(*args, **kwargs).dump()


def load(relationship, raw_data, replace=False, silent=False):
    return relationship_object.load(
        relationship=relationship,
        raw_data=raw_data,
        replace=replace,
        silent=silent
    )


class _RelationshipSerializer(_BaseSerializer):
    def __init__(self, relationship, related, **kwargs):
        super(_RelationshipSerializer, self).__init__(**kwargs)
        self.relationship = relationship
        self.related = related

    def _dump_primary(self):
        return resource_linkage.dump(
            relationship=self.relationship,
            related=self.related
        )

    def _dump_included(self):
        return []
