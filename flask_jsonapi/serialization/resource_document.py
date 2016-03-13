from . import document


def dump(*args, **kwargs):
    return _ResourceDocumentSerializer(*args, **kwargs).dump()


class _ResourceDocumentSerializer(document._DocumentSerializer):
    def __init__(self, resource, model, **kwargs):
        super(_ResourceDocumentSerializer, self).__init__(resource, **kwargs)
        self.model = model

    def _dump_primary(self):
        if self.model is not None:
            return self._dump_resource_object(
                resource=self.resource,
                model=self.model
            )

    def _dump_included(self):
        if self.model is not None:
            return list(self._iter_included_objects(model=self.model))
