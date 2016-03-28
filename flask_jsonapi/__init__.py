from flask import Blueprint, Flask, json

from .errors import JSONAPIException
from .resource_registry import ResourceRegistry

__version__ = '0.1.0 '


class JSONAPI(Flask):
    def __init__(self, *args, **kwargs):
        super(JSONAPI, self).__init__(*args, **kwargs)
        self._resource_registry = ResourceRegistry()
        self._init_error_handlers()

    def register_resource(self, resource):
        self._resource_registry.register(resource)

        blueprint = Blueprint(
            name=resource.type,
            import_name=__name__,
            url_prefix='/' + resource.type
        )

        resource_view = resource.view_cls.as_view('resource', resource=resource)

        blueprint.add_url_rule(
            '',
            defaults={'id': None},
            view_func=resource_view,
            methods=['GET']
        )
        blueprint.add_url_rule(
            '',
            view_func=resource_view,
            methods=['POST']
        )
        blueprint.add_url_rule(
            '/<id>',
            view_func=resource_view,
            methods=['GET', 'PATCH', 'DELETE']
        )

        for relationship in resource.relationships.values():
            related_view = relationship.related_view_cls.as_view(
                'related_' + relationship.name
            )
            relationship_view = relationship.relationship_view_cls.as_view(
                'relationship_' + relationship.name
            )

            blueprint.add_url_rule(
                '/<id>/' + relationship.name,
                view_func=related_view
            )
            blueprint.add_url_rule(
                '/<id>/relationships/' + relationship.name,
                view_func=relationship_view
            )

        self.register_blueprint(blueprint)

    def _init_error_handlers(self):
        self.register_error_handler(JSONAPIException, self._handle_jsonapi_exception)

    def _handle_jsonapi_exception(self, exception):
        return json.dumps(exception.get_json()), exception.status
