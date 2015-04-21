from .document import Document
from .schema import JSONAPISchema
from .views import blueprint


class JSONAPI(object):
    def __init__(self, app=None):
        self.app = app
        self._resources_by_type = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.register_blueprint(blueprint, url_prefix='')
        app.extensions['jsonapi'] = self

    def register(self, model, schema):
        self._resources_by_type[schema.Meta.type] = Resource(model, schema)


class Resource(object):
    def __init__(self, model, schema):
        self.model = model
        self.schema = schema
