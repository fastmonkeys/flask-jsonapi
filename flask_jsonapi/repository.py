import sqlalchemy
from sqlalchemy import orm

from . import exc


class SQLAlchemyRepository(object):
    def __init__(self, session):
        self.session = session

    def find(self, model_class, params):
        query = self.query(model_class)
        query = self._include_related(query, params.include)
        query = self._paginate(query, params.pagination)
        return query.all()

    def find_by_id(self, model_class, id, params):
        query = self.query(model_class).filter_by(id=id)
        query = self._include_related(query, params.include)
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

    def find_related_model(self, model, relationship, params=None):
        query = self._query_related(model, relationship)
        query = self._include_related(query, params.include)
        return query.first()

    def find_related_collection(self, model, relationship, params=None):
        query = self._query_related(model, relationship)
        query = self._include_related(query, params.include)
        query = self._paginate(query, params.pagination)
        return query.all()

    def _query_related(self, model, relationship):
        related_model_class = self.get_related_model_class(
            model.__class__,
            relationship
        )
        relationship_property = self._get_relationship_property(
            model.__class__,
            relationship
        )
        query = self.session.query(related_model_class)
        query._criterion = relationship_property._with_parent(model)
        query._order_by = relationship_property.order_by
        return query

    def get_related_model_class(self, model_class, relationship):
        prop = self._get_relationship_property(model_class, relationship)
        return prop.mapper.class_

    def get_attribute(self, model, attribute):
        return getattr(model, attribute)

    def get_id(self, model):
        return str(model.id)

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
            raise exc.InvalidRelationship(model_class, relationship)
