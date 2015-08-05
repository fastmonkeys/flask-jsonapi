import sqlalchemy
from sqlalchemy import orm

from . import exc


class SQLAlchemyRepository(object):
    def __init__(self, session):
        self.session = session

    def find(self, model_class, include=None, pagination=None):
        query = self.query(model_class)
        query = self._include_related(query, include)
        query = self._paginate(query, pagination)
        return query.all()

    def find_by_id(self, model_class, id, include=None):
        query = self.query(model_class).filter_by(id=id)
        query = self._include_related(query, include)
        try:
            return query.one()
        except orm.exc.NoResultFound:
            raise exc.ResourceNotFound(id)

    def find_count(self, model_class):
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
        model = self.model_class()
        self.session.add(model)
        return model

    def remove(self, model):
        self.session.remove(model)

    def replace_attributes(self, model, data):
        for key, value in data.items():
            setattr(model, key, value)

    def replace_has_one_relationship(self, model, name, value):
        setattr(model, name, value)

    def create_has_many_relationship(self, model, name, value):
        getattr(model, name).append(value)

    def replace_has_many_relationship(self, model, name, values):
        setattr(model, name, values)

    def remove_has_many_relationship(self, model, name, value):
        getattr(model, name).remove(value)

    def get_related(self, model, relationship):
        return getattr(model, relationship)

    def get_related_model_class(self, model_class, relationship):
        mapper = sqlalchemy.inspect(model_class)
        relationship_property = mapper.relationships[relationship]
        return relationship_property.mapper.class_

    def get_attribute(self, model, attribute):
        return getattr(model, attribute)

    def get_id(self, model):
        return str(model.id)

    def is_to_many_relationship(self, model_class, relationship):
        mapper = sqlalchemy.inspect(model_class)
        relationship_property = mapper.relationships[relationship]
        return relationship_property.uselist
