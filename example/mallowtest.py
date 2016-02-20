import marshmallow

from . import models
from .app import app


class BookSchema(marshmallow.Schema):
    title = marshmallow.fields.Str(required=True)
    author = marshmallow.fields.Raw(required=True)
    series = marshmallow.fields.Raw()
    date_published = marshmallow.fields.Date()


def serialize(book):
    schema = BookSchema()
    return schema.dump(book)


def deserialize(book):
    schema = BookSchema()
    return schema.load(book)


with app.app_context():
    book = models.Book.query.get(1)
    schema = BookSchema()
    print(schema.validate(book))

    # result = schema.dump(book)
    # data = result.data
    # data.update({'title': 'Foobar', 'author': None})
    # print(schema.load(data))
