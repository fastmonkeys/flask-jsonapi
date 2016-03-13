import itertools

from . import document


def dump(*args, **kwargs):
    return _ResourceCollectionDocumentSerializer(*args, **kwargs).dump()


class _ResourceCollectionDocumentSerializer(document._DocumentSerializer):
    def __init__(self, resource, models, **kwargs):
        super(_ResourceCollectionDocumentSerializer, self).__init__(
            resource,
            **kwargs
        )
        self.models = models

    def _dump_primary(self):
        return [
            self._dump_resource_object(resource=self.resource, model=model)
            for model in self.models
        ]

    def _dump_included(self):
        return list(
            itertools.chain.from_iterable(
                self._iter_included_objects(model=model)
                for model in self.models
            )
        )
