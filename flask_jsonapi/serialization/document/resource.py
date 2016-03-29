from .base import _BaseSerializer


def dump(*args, **kwargs):
    return _ResourceSerializer(*args, **kwargs).dump()


class _ResourceSerializer(_BaseSerializer):
    def __init__(self, resource, model, **kwargs):
        super(_ResourceSerializer, self).__init__(**kwargs)
        self.resource = resource
        self.model = model

    def _dump_primary(self):
        if self.model is not None:
            return self._dump_resource_object(
                resource=self.resource,
                model=self.model
            )

    def _dump_included(self):
        if self.model is not None:
            return list(self._iter_included_objects(
                resource=self.resource,
                model=self.model
            ))
