__version__ = '0.1.0 '

from .controller import Controller
from .resource_registry import ResourceRegistry
from .views import blueprint


class JSONAPI(object):
    def __init__(
        self,
        app=None,
        resource_registry=None,
        controller=None,
        url_prefix=''
    ):
        self.app = app
        if resource_registry is None:
            self.resources = ResourceRegistry()
        else:
            self.resources = resource_registry
        self.url_prefix = url_prefix

        if controller is None:
            self.controller = Controller(self.resources)
        else:
            self.controller = controller
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['jsonapi'] = self
        app.register_blueprint(blueprint, url_prefix=self.url_prefix)
