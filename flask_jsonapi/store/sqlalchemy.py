from __future__ import absolute_import

import sqlalchemy
from sqlalchemy import orm

from . import Store
from .. import exceptions


class SQLAlchemyStore(Store):
    def __init__(self, session):
        self.session = session

    def fetch(self, model_class, params=None):
        query = self.query(model_class)
        if params:
            query = self._include_related(query, params.include)
            query = self._paginate(query, params.pagination)
        return query.all()

    def fetch_one(self, model_class, id, params=None):
        query = self.query(model_class).filter_by(id=id)
        if params:
            query = self._include_related(query, params.include)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            raise exceptions.ObjectNotFound

    def get_related(self, obj, relationship):
        return getattr(obj, relationship)

    def fetch_related(self, obj, relationship, params=None):
        if self.is_to_many_relationship(obj.__class__, relationship):
            return self._fetch_many_related(obj, relationship, params)
        else:
            return self._fetch_one_related(obj, relationship, params)

    def _fetch_one_related(self, obj, relationship, params):
        query = self._query_related(obj, relationship)
        if params:
            query = self._include_related(query, params.include)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            return None

    def _fetch_many_related(self, obj, relationship, params):
        query = self._query_related(obj, relationship)
        if params:
            query = self._include_related(query, params.include)
            query = self._paginate(query, params.pagination)
        return query.all()

    def _query_related(self, obj, relationship):
        related_model_class = self.get_related_model_class(
            obj.__class__,
            relationship
        )
        relationship_property = self._get_relationship_property(
            obj.__class__,
            relationship
        )
        query = self.session.query(related_model_class)
        query = query.filter(relationship_property._with_parent(obj))
        if relationship_property.order_by:
            query = query.order_by(*relationship_property.order_by)
        return query

    def count(self, model_class):
        return self.query(model_class).count()

    def query(self, model_class):
        return self.session.query(model_class)

    def _include_related(self, query, include):
        paths = [] if include is None else include.paths
        for path in paths:
            option = orm.subqueryload(path[0])
            for relation in path[1:]:
                option = option.subqueryload(relation)
            query = query.options(option)
        return query

    def _paginate(self, query, pagination):
        if pagination is not None:
            query = query.offset(pagination.offset).limit(pagination.limit)
        return query

    def create(self, model_class):
        obj = self.model_class()
        self.session.add(obj)
        return obj

    def delete(self, obj):
        self.session.delete(obj)

    def replace_attribute(self, obj, name, value):
        setattr(obj, name, value)

    def replace_to_one_relationship(self, obj, name, value):
        setattr(obj, name, value)

    def create_to_many_relationship(self, obj, name, value):
        getattr(obj, name).append(value)

    def replace_to_many_relationship(self, obj, name, values):
        setattr(obj, name, values)

    def remove_to_many_relationship(self, obj, name, value):
        getattr(obj, name).remove(value)

    def get_related_model_class(self, model_class, relationship):
        prop = self._get_relationship_property(model_class, relationship)
        return prop.mapper.class_

    def get_attribute(self, obj, attribute):
        return getattr(obj, attribute)

    def get_id(self, obj):
        return str(obj.id)

    def is_to_many_relationship(self, model_class, relationship):
        mapper = sqlalchemy.inspect(model_class)
        return mapper.relationships[relationship].uselist

    def validate_attribute(self, model_class, attribute):
        pass

    def validate_relationship(self, model_class, relationship):
        self._get_relationship_property(model_class, relationship)

    def _get_relationship_property(self, model_class, relationship):
        mapper = sqlalchemy.inspect(model_class)
        try:
            return mapper.relationships[relationship]
        except KeyError:
            raise exceptions.InvalidRelationship(model_class, relationship)
