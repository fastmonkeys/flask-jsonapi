from __future__ import absolute_import

import sqlalchemy
from sqlalchemy import orm

from .. import exceptions


class SQLAlchemyStore(object):
    def __init__(self, session, model_class):
        self.session = session
        self.model_class = model_class

    def fetch(self, params=None):
        query = self.query
        if params:
            query = self._include_related(query, params.include)
            query = self._paginate(query, params.pagination)
        return query.all()

    def fetch_one(self, id, params=None):
        query = self.query.filter_by(id=id)
        if params:
            query = self._include_related(query, params.include)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            raise exceptions.ObjectNotFound

    def count_related(self, model, relationship):
        return self._query_related(model, relationship).count()

    def fetch_related(self, model, relationship, params=None):
        if self.is_to_many_relationship(relationship):
            return self._fetch_many_related(model, relationship, params)
        else:
            return self._fetch_one_related(model, relationship, params)

    def _fetch_one_related(self, model, relationship, params):
        query = self._query_related(model, relationship)
        if params:
            query = self._include_related(query, params.include)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            return None

    def _fetch_many_related(self, model, relationship, params):
        query = self._query_related(model, relationship)
        if params:
            query = self._include_related(query, params.include)
            query = self._paginate(query, params.pagination)
        return query.all()

    def _query_related(self, model, relationship):
        related_model_class = self.get_related_model_class(
            self.model_class,
            relationship
        )
        relationship_property = self._get_relationship_property(
            self.model_class,
            relationship
        )
        query = self.session.query(related_model_class)
        query = query.filter(relationship_property._with_parent(model))
        if relationship_property.order_by:
            query = query.order_by(*relationship_property.order_by)
        return query

    def count(self):
        return self.query.count()

    @property
    def query(self):
        return self.session.query(self.model_class)

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

    def create(self, id, fields):
        if id is not None and self._exists(self.model_class, id):
            raise exceptions.ObjectAlreadyExists
        instance = self.model_class(id=id, **fields)
        self.session.add(instance)
        self.session.commit()
        return instance

    def update(self, instance, fields):
        for name, value in fields.items():
            setattr(instance, name, value)
        self.session.commit()

    def _exists(self, id):
        query = self.session.query(self.model_class).filter_by(id=id)
        return self.session.query(query.exists()).scalar()

    def delete(self, instance):
        self.session.delete(instance)
        self.session.commit()

    def create_relationship(self, instance, relationship, values):
        collection = getattr(instance, relationship)
        for value in values:
            collection.append(value)
        self.session.commit()

    def delete_relationship(self, instance, relationship, values):
        collection = getattr(instance, relationship)
        for value in values:
            try:
                collection.remove(value)
            except ValueError:
                pass
        self.session.commit()

    def get_related_model_class(self, relationship):
        prop = self._get_relationship_property(self.model_class, relationship)
        return prop.mapper.class_

    def is_to_many_relationship(self, relationship):
        mapper = sqlalchemy.inspect(self.model_class)
        return mapper.relationships[relationship].uselist

    def validate_relationship(self, relationship):
        self._get_relationship_property(relationship)

    def _get_relationship_property(self, relationship):
        mapper = sqlalchemy.inspect(self.model_class)
        try:
            return mapper.relationships[relationship]
        except KeyError:
            raise exceptions.InvalidRelationship(self.model_class, relationship)
