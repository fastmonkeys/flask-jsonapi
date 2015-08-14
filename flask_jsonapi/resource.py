from . import exceptions
from .controller import Controller
from .paginator import PagedPaginator


class Resource(object):
    def __init__(
        self, type, model_class, store, attributes=None, relationships=None,
        paginator=None, allow_client_generated_ids=False
    ):
        self._registry = None
        self.type = type
        self.model_class = model_class
        self.store = store
        self.attributes = frozenset(attributes or [])
        self.relationships = frozenset(relationships or [])
        self.paginator = paginator if paginator else PagedPaginator()
        self._validate_field_names()
        self._validate_relationships()
        self.to_many_relationships = frozenset(
            relationship
            for relationship in self.relationships
            if self.store.is_to_many_relationship(
                self.model_class,
                relationship
            )
        )
        self.to_one_relationships = (
            self.relationships - self.to_many_relationships
        )
        self.allow_client_generated_ids = allow_client_generated_ids

    def _validate_field_names(self):
        self._check_reserved_field_names()
        self._check_field_naming_conflicts()

    def _validate_relationships(self):
        for relationship in self.relationships:
            self.store.validate_relationship(self.model_class, relationship)

    def _check_reserved_field_names(self):
        if {'id', 'type'} & self.fields:
            raise exceptions.FieldNamingConflict(
                "A resource cannot have an attribute or a relationship named "
                "'type' or 'id'."
            )

    def _check_field_naming_conflicts(self):
        if self.attributes & self.relationships:
            raise exceptions.FieldNamingConflict(
                'A resource cannot have an attribute and a relationship with '
                'the same name.'
            )

    @property
    def fields(self):
        return self.attributes | self.relationships

    def get_related_resource(self, relationship):
        related_model_class = self.store.get_related_model_class(
            self.model_class,
            relationship
        )
        return self._registry.by_model_class[related_model_class]

    def register(self, registry):
        if self._registry is not None:
            raise exceptions.ImproperlyConfigured(
                '{resource!r} has already been registered.'.format(
                    resource=self
                )
            )
        self._registry = registry

    def __repr__(self):
        return '<Resource {type}>'.format(type=self.type)
