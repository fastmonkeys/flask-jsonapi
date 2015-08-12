class Store(object):
    def fetch(self, model_class, params=None):
        raise NotImplementedError

    def fetch_one(self, model_class, id, params=None):
        raise NotImplementedError

    def fetch_related(self, model, relationship, params=None):
        raise NotImplementedError

    def count(self, model_class):
        raise NotImplementedError

    def create(self, model_class):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError

    def get_attribute(self, model, attribute):
        raise NotImplementedError

    def set_attribute(self, model, name, value):
        raise NotImplementedError

    def replace_to_one_relationship(self, model, name, value):
        raise NotImplementedError

    def create_to_many_relationship(self, model, name, value):
        raise NotImplementedError

    def replace_to_many_relationship(self, model, name, values):
        raise NotImplementedError

    def remove_to_many_relationship(self, model, name, value):
        raise NotImplementedError

    def get_related_model_class(self, model_class, relationship):
        raise NotImplementedError

    def get_id(self, model):
        raise NotImplementedError

    def is_to_many_relationship(self, model_class, relationship):
        raise NotImplementedError

    def validate_attribute(self, model_class, attribute):
        raise NotImplementedError

    def validate_relationship(self, model_class, relationship):
        raise NotImplementedError
