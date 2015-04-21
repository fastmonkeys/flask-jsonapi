from flask import Blueprint, current_app, jsonify

from .document import Document

blueprint = Blueprint('jsonapi', __name__)


@blueprint.after_request
def set_response_content_type(response):
    response.mimetype = 'application/vnd.api+json'
    return response


@blueprint.route('/<type>', methods=['GET'])
def get_many(type):
    resource = current_app.extensions['jsonapi']._resources_by_type[type]
    objects = resource.model.query.all()
    schema = resource.schema()
    document = Document(schema)
    return jsonify(document.dump(objects))


@blueprint.route('/<type>/<id>', methods=['GET'])
def get(type, id):
    pass


@blueprint.route('/<type>/<id>/<relationship>', methods=['GET'])
def get_related(type, id, relationship):
    pass


@blueprint.route('/<type>/<id>/links/<relationship>', methods=['GET'])
def get_relationship(type, id, relationship):
    pass


@blueprint.route('/<type>', methods=['POST'])
def create(type):
    pass


@blueprint.route('/<type>/<id>', methods=['PATCH'])
def update(type, id):
    pass


@blueprint.route('/<type>/<id>/links/<relationship>', methods=['PATCH'])
def update_relationship(type, id):
    pass


@blueprint.route('/<type>/<id>/links/<relationship>', methods=['POST'])
def add_to_relationship(type, id):
    pass


@blueprint.route('/<type>/<id>/links/<relationship>', methods=['DELETE'])
def delete_from_relationship(type, id):
    pass
