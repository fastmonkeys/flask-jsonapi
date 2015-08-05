from flask import Blueprint

blueprint = Blueprint('jsonapi', __name__)


@blueprint.after_request
def set_response_content_type(response):
    response.mimetype = 'application/vnd.api+json'
    return response


@blueprint.route('/<type>', methods=['GET'])
def get_many(type):
    pass


@blueprint.route('/<type>/<id>', methods=['GET'])
def get(type, id):
    pass


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
