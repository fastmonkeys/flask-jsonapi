import qstring
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from . import exc
from .params import FieldsParameter, IncludeParameter
from .serializer import Serializer

blueprint = Blueprint('jsonapi', __name__)


@blueprint.after_request
def set_response_content_type(response):
    response.mimetype = 'application/vnd.api+json'
    return response


@blueprint.errorhandler(exc.RequestError)
def handle_request_error(exc):
    statuses = {e['status'] for e in exc.errors}
    status = statuses.pop() if len(statuses) == 1 else BadRequest.code
    return jsonify(errors=exc.errors), status


@blueprint.route('/<type>', methods=['GET'])
def get_collection(type):
    jsonapi = current_app.extensions['jsonapi']
    try:
        resource = jsonapi.resources.by_type[type]
    except KeyError:
        raise exc.InvalidResource(type)
    params = qstring.nest(request.args.items(multi=True))
    pagination = resource.paginator.paginate(
        params=params.get('page', {}),
        count=resource.repository.find_count(resource.model_class)
    )
    fields = FieldsParameter(jsonapi.resources, params.get('fields'))
    include = IncludeParameter(jsonapi.resources, type, params.get('include'))
    models = resource.repository.find(
        resource.model_class,
        include=include,
        pagination=pagination
    )
    serializer = Serializer(
        jsonapi.resources,
        type,
        include=include,
        fields=fields,
        pagination=pagination
    )
    data = serializer.dump(models, many=True)
    return jsonify(data)


@blueprint.route('/<type>/<id>', methods=['GET'])
def get(type, id):
    jsonapi = current_app.extensions['jsonapi']
    try:
        resource = jsonapi.resources.by_type[type]
    except KeyError:
        raise exc.InvalidResource(type)
    params = qstring.nest(request.args.items(multi=True))
    fields = FieldsParameter(jsonapi.resources, params.get('fields'))
    include = IncludeParameter(jsonapi.resources, type, params.get('include'))
    model = resource.repository.find_by_id(
        resource.model_class,
        id=id,
        include=include
    )
    serializer = Serializer(
        jsonapi.resources,
        type,
        include=include,
        fields=fields
    )
    data = serializer.dump(model)
    return jsonify(data)


@blueprint.route('/<type>/<id>/<relationship>', methods=['GET'])
def get_related(type, id, relationship):
    pass


@blueprint.route('/<type>/<id>/relationships/<relationship>', methods=['GET'])
def get_relationship(type, id, relationship):
    pass


@blueprint.route('/<type>', methods=['POST'])
def create(type):
    pass


@blueprint.route('/<type>/<id>', methods=['PATCH'])
def update(type, id):
    pass


@blueprint.route(
    '/<type>/<id>/relationships/<relationship>',
    methods=['PATCH']
)
def update_relationship(type, id):
    pass


@blueprint.route('/<type>/<id>/relationships/<relationship>', methods=['POST'])
def add_to_relationship(type, id):
    pass


@blueprint.route(
    '/<type>/<id>/relationships/<relationship>',
    methods=['DELETE']
)
def delete_from_relationship(type, id):
    pass
