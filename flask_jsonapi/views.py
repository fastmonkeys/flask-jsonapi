from flask import Blueprint, current_app, jsonify
from werkzeug.exceptions import BadRequest
from werkzeug.local import LocalProxy

from . import errors

blueprint = Blueprint('jsonapi', __name__)


@blueprint.after_request
def set_response_content_type(response):
    response.mimetype = 'application/vnd.api+json'
    return response


@blueprint.errorhandler(errors.Error)
def handle_request_error(error):
    statuses = {e['status'] for e in error.errors}
    status = statuses.pop() if len(statuses) == 1 else BadRequest.code
    return jsonify(errors=error.errors), status


controller = LocalProxy(lambda: current_app.extensions['jsonapi'].controller)


@blueprint.route('/<type>', methods=['GET'])
def fetch(type):
    return controller.fetch(type)


@blueprint.route('/<type>/<id>', methods=['GET'])
def fetch_one(type, id):
    return controller.fetch_one(type, id)


@blueprint.route('/<type>/<id>/<relationship>', methods=['GET'])
def fetch_related(type, id, relationship):
    return controller.fetch_related(type, id, relationship)


@blueprint.route('/<type>/<id>/relationships/<relationship>', methods=['GET'])
def fetch_relationship(type, id, relationship):
    return controller.fetch_relationship(type, id, relationship)


@blueprint.route('/<type>', methods=['POST'])
def create(type):
    return controller.create(type)


@blueprint.route('/<type>/<id>', methods=['DELETE'])
def delete(type, id):
    return controller.delete(type, id)


@blueprint.route('/<type>/<id>', methods=['PATCH'])
def update(type, id):
    return controller.update(type, id)


@blueprint.route(
    '/<type>/<id>/relationships/<relationship>',
    methods=['PATCH']
)
def update_relationship(type, id, relationship):
    return controller.update_relationship(type, id, relationship)


@blueprint.route('/<type>/<id>/relationships/<relationship>', methods=['POST'])
def create_relationship(type, id, relationship):
    return controller.create_relationship(type, id, relationship)


@blueprint.route(
    '/<type>/<id>/relationships/<relationship>',
    methods=['DELETE']
)
def delete_relationship(type, id, relationship):
    return controller.delete_relationship(type, id, relationship)
