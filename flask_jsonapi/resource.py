from . import exc


class Resource(object):
    def __init__(
        self, type, model_class, repository, attributes=None,
        relationships=None
    ):
        self.type = type
        self.model_class = model_class
        self.repository = repository
        self.attributes = frozenset(attributes or [])
        self.relationships = frozenset(relationships or [])
        self._validate_field_names()

    def _validate_field_names(self):
        self._check_reserved_field_names()
        self._check_field_naming_conflicts()

    def _check_reserved_field_names(self):
        if {'id', 'type'} & self.fields:
            raise exc.FieldNamingConflict(
                "A resource cannot have an attribute or a relationship named "
                "'type' or 'id'."
            )

    def _check_field_naming_conflicts(self):
        if self.attributes & self.relationships:
            raise exc.FieldNamingConflict(
                'A resource cannot have an attribute and a relationship with '
                'the same name.'
            )

    @property
    def fields(self):
        return self.attributes | self.relationships

    def __repr__(self):
        return '<Resource {type}>'.format(type=self.type)
