import qstring
from flask import MethodView, abort, current_app, json, request
from werkzeug.urls import url_encode

from .. import errors, exceptions, serialization
from ..params import Parameters
from ..request_parser import RequestParser


# users

class ResourceCollectionView(MethodView):
    def get(self):
        pass

    def post(self):
        pass


class ResourceView(MethodView):
    def get(self, id):
        pass

    def patch(self, id):
        pass

    def delete(self, id):
        pass


class RelatedResourceView(MethodView):
    def get(self, id):
        pass


class RelatedResourceCollectionView(MethodView):
    def get(self, id):
        pass


class ToOneRelationshipView(MethodView):
    def get(self, id):
        pass

    def patch(self, id):
        pass


class ToManyRelationshipView(MethodView):
    def get(self, id):
        pass

    def patch(self, id):
        pass

    def post(self, id):
        pass

    def delete(self, id):
        pass



# books.collection
# ----------------
#    GET /books
#   POST /books

# books.???
# ---------
#    GET /books/:id
#  PATCH /books/:id
# DELETE /books/:id

view = ResourceView.as_view('books', resource=books)
blueprint = Blueprint('books', url_prefix='/books')
blueprint.add_url_rule('/<id>', view_func=view, methods=['GET', 'PATCH', 'DELETE'])


# books.related_author
# --------------------
#    GET /books/:id/author

# books.related_chapters
# ----------------------
#    GET /books/:id/chapters


# books.relationship_author
# -------------------------
#    GET /books/:id/relationships/author
#  PATCH /books/:id/relationships/author

# books.related_chapters
# ----------------------
#    GET /books/:id/chapters
#  PATCH /books/:id/chapters
#   POST /books/:id/chapters
# DELETE /books/:id/chapters
