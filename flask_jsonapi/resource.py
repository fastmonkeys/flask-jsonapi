from . import exceptions
from .paginator import PagedPaginator


class Resource(object):
    def __init__(self, type, model_class, store, paginator=None):
        self._registry = None
        self.type = type
        self.model_class = model_class
        self.store = store
        self.fields = {}
        self.attributes = {}
        self.relationships = {}
        self.paginator = paginator if paginator else PagedPaginator()
        self.allow_client_generated_ids = False

    def add_attribute(self, *args, **kwargs):
        field = Attribute(self, *args, **kwargs)
        self._add_field(field)
        self.attributes[field.name] = field

    def add_relationship(self, *args, **kwargs):
        field = Relationship(self, *args, **kwargs)
        self._add_field(field)
        self.relationships[field.name] = field

    def _add_field(self, field):
        if field.name in self.fields:
            raise exceptions.FieldNamingConflict(
                'The resource already has a field called {field!r}.'.format(
                    field=field.name
                )
            )
        self.fields[field.name] = field

    @property
    def required_attributes(self):
        for attribute in self.attributes.values():
            if attribute.required:
                yield attribute

    @property
    def required_relationships(self):
        for relationship in self.relationships.values():
            if relationship.required:
                yield relationship

    def register(self, registry):
        if self._registry is not None:
            raise exceptions.ResourceAlreadyRegistered(
                '{resource!r} has already been registered.'.format(
                    resource=self
                )
            )
        self._registry = registry

    def __repr__(self):
        return '<{cls} type={type!r}>'.format(
            cls=self.__class__.__name__,
            type=self.type
        )


class Field(object):
    def __init__(self, parent_resource, name, required=False, validator=None):
        self.parent_resource = parent_resource
        self.name = name
        self.required = required
        self.validator = validator
        self._check_name()

    def _check_name(self):
        if self.name in {'id', 'type'}:
            raise exceptions.FieldNamingConflict(
                "A resource cannot have a field named 'type' or 'id'."
            )

    def __repr__(self):
        return '<{cls} name={name!r}>'.format(
            cls=self.__class__.__name__,
            name=self.name
        )


class Attribute(Field):
    pass


class Relationship(Field):
    def __init__(
        self, parent_resource, name, allow_include=None, allow_full_replacement=False, **kwargs):
        super(Relationship, self).__init__(parent_resource, name, **kwargs)
        self.many = self.parent_resource.store.is_to_many_relationship(
            self.parent_resource.model_class,
            self.name
        )
        self.allow_include = (
            not self.many if allow_include is None else allow_include
        )
        self.allow_full_replacement = allow_full_replacement

    @property
    def model_class(self):
        return self.parent_resource.store.get_related_model_class(
            self.parent_resource.model_class,
            self.name
        )

    @property
    def resource(self):
        return self.parent_resource._registry.by_model_class[self.model_class]

    @property
    def type(self):
        return self.resource.type
