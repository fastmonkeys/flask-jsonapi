from marshmallow import validate

from flask_jsonapi import JSONAPI, Schema, fields
from flask_jsonapi.controllers.postgresql import PostgreSQLController
from flask_jsonapi.resource import Resource
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore

from . import models

jsonapi = JSONAPI(controller_class=PostgreSQLController)


class SeriesSchema(Schema):
    id = fields.Str()
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    books = fields.Relationship(type_='books', many=True, allow_include=True)


class AuthorSchema(Schema):
    id = fields.Str()
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    date_of_birth = fields.Date(required=True)
    date_of_death = fields.Date()
    books = fields.Relationship(type_='books', many=True)


class BookSchema(Schema):
    id = fields.Str()
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    date_published = fields.Date(required=True)
    author = fields.Relationship(type_='authors', required=True)
    chapters = fields.Relationship(
        type_='authors',
        allow_include=True,
        allow_full_replacement=True,
        many=True
    )
    series = fields.Relationship(type_='series')
    stores = fields.Relationship(
        type_='stores',
        allow_include=True,
        allow_full_replacement=True
    )


class ChapterSchema(Schema):
    id = fields.Str()
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    ordering = fields.Int('ordering')
    book = fields.Relationship(type_='books')


class StoreSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1))
    books = fields.Relationship(type_='books')


series = Resource(
    type_='series',
    schema=SeriesSchema,
    store=SQLAlchemyStore(models.Series)
)

authors = Resource(
    type_='authors',
    schema=AuthorSchema,
    store=SQLAlchemyStore(models.Author),
    allow_client_generated_ids=True
)

books = Resource(
    type_='books',
    schema=BookSchema,
    store=SQLAlchemyStore(models.Book),
)

chapters = Resource(
    type_='chapters',
    schema=ChapterSchema,
    store=SQLAlchemyStore(models.Chapter),
)

stores = Resource(
    type_='stores',
    schema=StoreSchema,
    store=SQLAlchemyStore(models.Store),
)

jsonapi.resources.register(series)
jsonapi.resources.register(authors)
jsonapi.resources.register(books)
jsonapi.resources.register(chapters)
jsonapi.resources.register(stores)
