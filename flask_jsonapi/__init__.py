__version__ = '0.1.0 '

from .views import blueprint
from .resource_registry import ResourceRegistry


class JSONAPI(object):
    def __init__(self, app=None, url_prefix=''):
        self.app = app
        self.resource_registry = ResourceRegistry()
        self.url_prefix = url_prefix
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['jsonapi'] = self
        app.register_blueprint(blueprint, url_prefix=self.url_prefix)

    def register_resource(self, resource_class):
        self.resource_registry.add(resource_class)
