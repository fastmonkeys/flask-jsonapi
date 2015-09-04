from . import exceptions
from .paginator import PagedPaginator


class Resource(object):
    def __init__(
        self,
        type,
        store,
        model_class,
        fields,
        paginator=None,
        allow_client_generated_ids=False
    ):
        self._registry = None
        self.type = type
        self.model_class = model_class
        self.store = store
        self.fields = {}
        self.attributes = {}
        self.relationships = {}
        self._add_fields(fields)
        self.paginator = PagedPaginator() if paginator is None else paginator
        self.allow_client_generated_ids = allow_client_generated_ids

    def _add_fields(self, fields):
        for field in fields:
            self._add_field(field)

    def _add_field(self, field):
        if not isinstance(field, Field):
            raise TypeError('expected Field')

        if field.name in self.fields:
            raise exceptions.FieldNamingConflict(
                'The resource already has a field called {field!r}.'.format(
                    field=field.name
                )
            )

        field.bind(self)
        self.fields[field.name] = field
        if isinstance(field, Attribute):
            self.attributes[field.name] = field
        if isinstance(field, Relationship):
            self.relationships[field.name] = field

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
    def __init__(self, name, required=False, validator=None):
        self.name = name
        self.required = required
        self.validator = (lambda v: v) if validator is None else validator
        self._check_name()

    def bind(self, parent):
        self.parent = parent

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
        self,
        name,
        allow_include=None,
        allow_full_replacement=False,
        **kwargs
    ):
        super(Relationship, self).__init__(name, **kwargs)
        self.allow_include = allow_include
        self.allow_full_replacement = allow_full_replacement

    def bind(self, *args, **kwargs):
        super(Relationship, self).bind(*args, **kwargs)
        self.many = self.parent.store.is_to_many_relationship(
            self.parent.model_class,
            self.name
        )
        if self.allow_include is None:
            self.allow_include = not self.many

    @property
    def model_class(self):
        return self.parent.store.get_related_model_class(
            self.parent.model_class,
            self.name
        )

    @property
    def resource(self):
        return self.parent._registry.by_model_class[self.model_class]

    @property
    def type(self):
        return self.resource.type
