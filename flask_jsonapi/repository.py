import sqlalchemy


class SQLAlchemyRepository(object):
    def __init__(self, session):
        self.session = session

    def query(self, model_cls):
        return self.session.query(model_cls)

    def find(self, model_cls):
        return self.query(model_cls)

    def find_by_id(self, model_cls, id):
        try:
            return self.query(model_cls).filter_by(id=id).one()
        except orm.exc.NoResultFound:
            raise ResourceNotFound(id)

    def create(self, model_cls):
        model = self.model_cls()
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

    def get_id(self, model):
        pass

    def get_related_model_class(self, model_class, relationship):
        mapper = sqlalchemy.inspect(model_class)
        relationship_property = mapper.relationships[relationship]
        return relationship_property.mapper.class_
