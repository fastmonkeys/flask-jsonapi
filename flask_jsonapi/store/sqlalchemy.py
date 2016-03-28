from __future__ import absolute_import

import sqlalchemy
from sqlalchemy import orm

from .. import exceptions
from ..datastructures import Pagination


class SQLAlchemyStore(object):
    def __init__(self, session, model_class):
        self.session = session
        self.model_class = model_class

    def fetch_one(self, id, **kwargs):
        try:
            return self._fetch_one(query=self.query.filter_by(id=id), **kwargs)
        except orm.exc.NoResultFound:
            raise exceptions.ObjectNotFound

    def fetch_many(self, **kwargs):
        return self._fetch_many(query=self.query(), **kwargs)

    def fetch_one_related(self, model, relationship, **kwargs):
        try:
            return self._fetch_one(query=self.query.filter_by(id=id), **kwargs)
        except orm.exc.NoResultFound:
            return None

    def fetch_many_related(self, model, relationship, **kwargs):
        return self._fetch_many(
            query=self._query_related(model, relationship),
            **kwargs
        )

    def _fetch_one(self, query, include=None):
        query = self._include_related(query, include=include)
        return query.one()

    def _fetch_many(self, query, include=None, page=None):
        query = self._include_related(query, include=include)
        query = self._paginate(query, page=page)
        return Pagination(
            page=page,
            total=query.count(),
            models=query.all()
        )

    def _query_related(self, model, relationship):
        mapper = sqlalchemy.inspect(self.model_class)
        relationship_property = mapper.relationships[relationship]
        related_model_class = relationship_property.mapper.class_
        query = self.session.query(related_model_class)
        query = query.filter(relationship_property._with_parent(model))
        if relationship_property.order_by:
            query = query.order_by(*relationship_property.order_by)
        return query

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

    def _paginate(self, query, page):
        if page is not None:
            query = query.offset((page.number - 1) * page.size)
            query = query.limit(page.size)
        return query

    def create(self, id, fields):
        if id is not None and self._exists(self.model_class, id):
            raise exceptions.ObjectAlreadyExists
        model = self.model_class(id=id, **fields)
        self.session.add(model)
        self.session.commit()
        return model

    def update(self, model, fields):
        for name, value in fields.items():
            setattr(model, name, value)
        self.session.commit()

    def _exists(self, id):
        query = self.session.query(self.model_class).filter_by(id=id)
        return self.session.query(query.exists()).scalar()

    def delete(self, model):
        self.session.delete(model)
        self.session.commit()

    def create_relationship(self, model, relationship, values):
        collection = getattr(model, relationship)
        for value in values:
            collection.append(value)
        self.session.commit()

    def delete_relationship(self, model, relationship, values):
        collection = getattr(model, relationship)
        for value in values:
            try:
                collection.remove(value)
            except ValueError:
                pass
        self.session.commit()
