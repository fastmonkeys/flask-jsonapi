import itertools

from .base import _BaseSerializer


def dump(*args, **kwargs):
    return _ResourceCollectionSerializer(*args, **kwargs).dump()


class _ResourceCollectionSerializer(_BaseSerializer):
    def __init__(self, resource, models, **kwargs):
        super(_ResourceCollectionSerializer, self).__init__(**kwargs)
        self.resource = resource
        self.models = models

    def _dump_primary(self):
        return [
            self._dump_resource_object(resource=self.resource, model=model)
            for model in self.models
        ]

    def _dump_included(self):
        iter_included_objects = itertools.chain.from_iterable(
            self._iter_included_objects(resource=self.resource, model=model)
            for model in self.models
        )
        return list(iter_included_objects)
