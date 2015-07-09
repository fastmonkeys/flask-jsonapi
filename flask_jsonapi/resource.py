import six
import sqlalchemy as sa
from sqlalchemy import orm

from . import exc


class _ResourceOptions(object):
    RESERVED_FIELD_NAMES = frozenset(['id', 'type'])

    def __init__(self, resource_class, options=None):
        self.resource_class = resource_class
        self.type = getattr(options, 'type', None)
        self.model_class = getattr(options, 'model_class', None)
        self._attributes = frozenset()
        self._relationships = frozenset()
        self.attributes = getattr(options, 'attributes', [])
        self.relationships = getattr(options, 'relationships', [])

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not value:
            raise exc.ImproperlyConfigured(
                "{resource_class}.Meta.type must be specified.".format(
                    resource_class=self.resource_class.__name__
                )
            )
        self._type = value

    @property
    def model_class(self):
        return self._model_class

    @model_class.setter
    def model_class(self, value):
        if not value:
            raise exc.ImproperlyConfigured(
                "{resource_class}.Meta.model_class must be specified.".format(
                    resource_class=self.resource_class.__name__
                )
            )
        try:
            sa.orm.class_mapper(value)
        except (orm.exc.UnmappedClassError, sa.exc.ArgumentError):
            raise exc.ImproperlyConfigured(
                "{resource_class}.Meta.model_class must be a class mapped by "
                "SQLAlchemy.".format(
                    resource_class=self.resource_class.__name__
                )
            )
        self._model_class = value

    @property
    def fields(self):
        return self.attributes | self.relationships

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = self._validate_field_names(attributes)

    @property
    def relationships(self):
        return self._relationships

    @relationships.setter
    def relationships(self, relationships):
        self._relationships = self._validate_field_names(relationships)

    def _validate_field_names(self, field_names):
        return frozenset(
            self._validate_field_name(field_name)
            for field_name in field_names
        )

    def _validate_field_name(self, field_name):
        if field_name in self.RESERVED_FIELD_NAMES:
            raise exc.ImproperlyConfigured(
                "{resource_class}: a resource cannot have an attribute or a "
                "relationship named 'type' or 'id'.".format(
                    resource_class=self.resource_class.__name__
                )
            )
        if field_name in self.fields:
            raise exc.ImproperlyConfigured(
                '{resource_class}: a resource cannot have an attribute and a '
                'relationship with the same name ({field_name!r}).'.format(
                    resource_class=self.resource_class.__name__,
                    field_name=field_name
                )
            )
        return field_name

    def __repr__(self):
        return '<{cls} resource_class={resource_class!r}>'.format(
            cls=self.__class__.__name__,
            resource_class=self.resource_class
        )


class _ResourceMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super(_ResourceMeta, mcs).__new__(mcs, name, bases, attrs)

        if bases == (_BaseResource,):
            return new_class

        options = _ResourceOptions(new_class, getattr(new_class, 'Meta', None))
        new_class._meta = options

        return new_class


class _BaseResource(object):
    def __init__(self, session, model):
        self.session = session
        self.model = model

    @classmethod
    def find(cls, session):
        query = session.query(cls.model_cls)
        for model in query:
            yield cls(session, model)

    @classmethod
    def find_by_id(cls, session, id):
        try:
            model = session.query(cls.model_cls).filter_by(id=id).one()
        except orm.exc.NoResultFound:
            raise ResourceNotFound(id)
        return cls(session, model)

    @classmethod
    def create(cls, session):
        model = cls.model_cls()
        session.add(model)
        return cls(session, model)

    def remove(self):
        self.session.remove(self.model)

    def replace_attributes(self, data):
        pass

    def replace_has_one_relationship(self, name, value):
        pass

    def create_has_many_relationship(self, name, value):
        pass

    def replace_has_many_relationship(self, name, values):
        pass

    def remove_has_many_relationship(self, name, value):
        pass


class Resource(six.with_metaclass(_ResourceMeta, _BaseResource)):
    pass
