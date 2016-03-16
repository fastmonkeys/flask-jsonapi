from . import _parsers, link_builder, resource_linkage
from ..errors import FullReplacementDisallowed, JSONAPIException


def dump(relationship, model):
    data = {
        'links': {
            'self': link_builder.relationship_self_link(
                relationship=relationship,
                model=model
            ),
            'related': link_builder.relationship_related_link(
                relationship=relationship,
                model=model
            )
        }
    }
    if relationship.allow_include:
        data['data'] = resource_linkage.dump(
            relationship=relationship,
            related=getattr(model, relationship.name),
        )
    return data


def load(relationship, raw_data, replace=False):
    parser = _RelationshipObject(relationship, replace=replace)
    return parser(raw_data)['data']


class _RelationshipObject(_parsers.Object):
    def __init__(self, relationship, replace):
        super(_RelationshipObject, self).__init__(
            properties={
                'data': lambda raw_data: resource_linkage.load(
                    relationship=relationship,
                    raw_data=raw_data
                )
            },
            required=['data']
        )
        self.relationship = relationship
        self.replace = replace

    def __call__(self, raw_data):
        self._check_full_replacement()
        return super(_RelationshipObject, self).__call__(raw_data)

    def _check_full_replacement(self):
        if (
            self.replace and
            self.relationship.many and
            not self.relationship.allow_full_replacement
        ):
            error = FullReplacementDisallowed(
                relationship=self.relationship.name,
                source_path=[]
            )
            raise JSONAPIException(error)
