from . import exceptions


class Resource(object):
    def __init__(
        self,
        type,
        store,
        fields,
        attribute_serializer=None,
        attribute_deserializer=None,
        allow_client_generated_ids=False
    ):
        self._registry = None
        self.type = type
        self.store = store
        self.fields = {}
        self.attributes = {}
        self.relationships = {}
        self._add_fields(fields)
        self.allow_client_generated_ids = allow_client_generated_ids
        self.attribute_serializer = attribute_serializer
        self.attribute_deserializer = attribute_deserializer
        self.id_deserializer = int
        self.max_page_size = 100
        self.default_page_size = 20

    def _add_fields(self, fields):
        for field in fields:
            self._add_field(field)

    def _add_field(self, field):
        self._validate_field(field)

        field.bind(self)
        self.fields[field.name] = field
        if isinstance(field, Attribute):
            self.attributes[field.name] = field
        if isinstance(field, Relationship):
            self.relationships[field.name] = field

    def _validate_field(self, field):
        if not isinstance(field, Field):
            raise TypeError('expected Field')

        if field.name in self.fields:
            raise ValueError(
                'The resource already has a field called {field!r}.'.format(
                    field=field.name
                )
            )

        if field.name in {'id', 'type'}:
            raise ValueError(
                "A resource cannot have a field named 'type' or 'id'."
            )

    def serialize_attributes(self, data):
        if self.attribute_serializer:
            return self.attribute_serializer(data)
        return data

    def deserialize_attributes(self, data):
        if self.attribute_deserializer:
            return self.attribute_deserializer(data)
        return data

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
    def __init__(self, name):
        self.name = name

    def bind(self, parent):
        self.parent = parent

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
        type,
        many,
        allow_include=None,
        **kwargs
    ):
        super(Relationship, self).__init__(name, **kwargs)
        self.type = type
        self.many = many
        self.allow_include = allow_include

    @property
    def resource(self):
        return self.parent._registry.by_type[self.type]


class ToOneRelationship(Relationship):
    def __init__(self, name, type, **kwargs):
        super(ToOneRelationship, self).__init__(
            name=name,
            type=type,
            many=False,
            **kwargs
        )
        if self.allow_include is None:
            self.allow_include = True


class ToManyRelationship(Relationship):
    def __init__(self, name, type, allow_full_replacement=False, **kwargs):
        super(ToManyRelationship, self).__init__(
            name=name,
            type=type,
            many=True,
            **kwargs
        )
        if self.allow_include is None:
            self.allow_include = False
        self.allow_full_replacement = allow_full_replacement
