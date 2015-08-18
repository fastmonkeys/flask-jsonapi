__version__ = '0.1.0 '

from .controllers.default import DefaultController
from .resource_registry import ResourceRegistry
from .views import blueprint


class JSONAPI(object):
    def __init__(
        self,
        app=None,
        controller_class=DefaultController,
        url_prefix=''
    ):
        self.app = app
        self.resources = ResourceRegistry()
        self.url_prefix = url_prefix
        self.controller = controller_class(resource_registry=self.resources)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['jsonapi'] = self
        app.register_blueprint(blueprint, url_prefix=self.url_prefix)
