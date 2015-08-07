import qstring
from flask import jsonify, request

from .serializer import Serializer


class Controller(object):
    def __init__(self, resource_registry, request, resource):
        self.resource_registry = resource_registry
        self.request = request
        self.resource = resource
        self.serializer = Serializer(resource_registry)

    def build_params(
        self, type, allow_fields=False, allow_include=False,
        allow_pagination=False
    ):
        return Parameters(
            self.resource_registry,
            type,
            params=qstring.nest(request.args.items(multi=True)),
            allow_fields=allow_fields,
            allow_include=allow_include,
            allow_pagination=allow_pagination
        )

    def get_model(self, id):
        params = self.build_params(allow_fields=True, allow_include=True)
        model = self.resource.repository.find_by_id(
            self.resource.model_class,
            id,
            params
        )
        data = self.serializer.dump(model, params)
        return jsonify(data)

    def get_collection(self):
        params = self.build_params(
            self.resource.type,
            allow_fields=True,
            allow_include=True,
            allow_pagination=True
        )
        models = self.resource.repository.find(
            self.resource.model_class,
            params
        )
        data = self.serializer.dump(models, params, many=True)
        return jsonify(data)

    def get_related_model(self, id, relation):
        model = self.resource.repository.find_by_id(
            self.resource.model_class,
            id
        )
        related_model_class = self.resource.repository.get_related_model_class(model.__class__, relation)
        related_resource = self.resource_registry.by_model_class[related_model_class]
        params = self.build_params(
            related_resource.type,
            allow_fields=True,
            allow_include=True
        )
        related_model = self.resource.repository.get_related_model(
            model,
            relation,
            params
        )
        data = self.serializer.dump(related_model, params)
        return jsonify(data)

    def get_related_collection(self, id, relation):
        model = self.resource.repository.find_by_id(
            self.resource.model_class,
            id
        )
        related_model_class = self.resource.repository.get_related_model_class(model.__class__, relation)
        related_resource = self.resource_registry.by_model_class[related_model_class]
        params = self.build_params(
            related_resource.type,
            allow_fields=True,
            allow_include=True,
            allow_pagination=True
        )
        related_models = self.resource.repository.get_related_collection(
            model,
            relation,
            params
        )
        data = self.serializer.dump(related_models, params, many=True)
        return jsonify(data)
