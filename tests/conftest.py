import json
import os
from datetime import datetime

import pytest
from bunch import Bunch
from flask import Response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from flask_jsonapi import JSONAPI
from flask_jsonapi.resource import (
    Attribute,
    Resource,
    ToManyRelationship,
    ToOneRelationship
)
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FANTASY_DATABASE_FILENAME = os.path.join(
    PROJECT_ROOT,
    'node_modules',
    'fantasy-database',
    'data.json'
)


class JSONResponse(Response):
    @property
    def json(self):
        return json.loads(self.data.decode('utf8'))


@pytest.yield_fixture
def app(db, resources):
    app = JSONAPI(__name__)

    app.config['SERVER_NAME'] = 'example.com'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True

    db.init_app(app)

    for resource in resources.values():
        app.register_resource(resource)

    app.response_class = JSONResponse
    with app.app_context():
        yield app


@pytest.fixture
def db():
    return SQLAlchemy()


@pytest.fixture
def resource_registry(app):
    return app._resource_registry


@pytest.fixture
def resources(db, models):
    bunch = Bunch()

    class SeriesSchema(Schema):
        title = fields.Str(required=True)

    bunch.series = Resource(
        type='series',
        fields=[
            Attribute('title'),
            ToManyRelationship('books', type='books', allow_include=True),
        ],
        store=SQLAlchemyStore(session=db.session, model_class=models.Series),
    )

    class AuthorSchema(Schema):
        name = fields.Str(required=True)
        date_of_birth = fields.Date(required=True)
        date_of_death = fields.Date()

    bunch.authors = Resource(
        type='authors',
        fields=[
            Attribute('name'),
            Attribute('date_of_birth'),
            Attribute('date_of_death'),
            ToManyRelationship('books', type='books'),
        ],
        store=SQLAlchemyStore(session=db.session, model_class=models.Author),
        attribute_serializer=build_attribute_serializer(AuthorSchema),
        allow_client_generated_ids=True,
    )

    class BookSchema(Schema):
        title = fields.Str(required=True)
        date_published = fields.Date(required=True)

    bunch.books = Resource(
        type='books',
        fields=[
            Attribute('title'),
            Attribute('date_published'),
            ToOneRelationship('author', type='authors'),
            ToManyRelationship(
                'chapters',
                type='chapters',
                allow_include=True
            ),
            ToOneRelationship('series', type='series'),
            ToManyRelationship(
                'stores',
                type='stores',
                allow_full_replacement=True
            ),
        ],
        attribute_serializer=build_attribute_serializer(BookSchema),
        attribute_deserializer=build_attribute_deserializer(BookSchema),
        store=SQLAlchemyStore(session=db.session, model_class=models.Book),
    )

    class ChapterSchema(Schema):
        title = fields.Str(required=True)
        ordering = fields.Int(required=True)

    bunch.chapters = Resource(
        type='chapters',
        fields=[
            Attribute('title'),
            Attribute('ordering'),
            ToOneRelationship('book', type='books'),
        ],
        store=SQLAlchemyStore(session=db.session, model_class=models.Chapter),
    )

    class StoreSchema(Schema):
        name = fields.Str(required=True)

    bunch.stores = Resource(
        type='stores',
        fields=[
            Attribute('name'),
            ToManyRelationship('books', type='books'),
        ],
        store=SQLAlchemyStore(session=db.session, model_class=models.Store),
    )

    return bunch


@pytest.yield_fixture
def fantasy_database(app, db):
    with open(FANTASY_DATABASE_FILENAME, 'r') as f:
        data = json.loads(f.read())

    db.create_all()

    connection = db.engine.connect()
    for table in db.metadata.sorted_tables:
        rows = data[table.name]

        for row in rows:
            for column, value in row.items():
                if isinstance(table.columns[column].type, db.Date) and value:
                    row[column] = datetime.strptime(value, '%Y-%m-%d').date()

        connection.execute(table.insert(), rows)
        # if table.name != 'books_stores':
        #     # connection.execute(
        #     #     'ALTER SEQUENCE {table}_id_seq RESTART WITH {num_rows}'.format(
        #     #         table=table.name,
        #     #         num_rows=len(rows) + 1
        #     #     )
        #     # )
        #     connection.execute(
        #         'UPDATE sqlite_sequence SET seq = :seq WHERE name = :table',
        #         seq=len(rows) + 1,
        #         table=table.name
        #     )

    yield

    for table in reversed(db.metadata.sorted_tables):
        db.session.execute('DROP TABLE {0}'.format(table.name))
    db.session.commit()

    db.session.close_all()
    db.engine.dispose()


@pytest.fixture
def models(db):
    book_store = db.Table(
        'books_stores',
        db.Column(
            'book_id',
            db.Integer,
            db.ForeignKey('books.id', ondelete='CASCADE'),
            nullable=False
        ),
        db.Column(
            'store_id',
            db.Integer,
            db.ForeignKey('stores.id', ondelete='CASCADE'),
            nullable=False
        ),
    )

    class Series(db.Model):
        __tablename__ = 'series'
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.Text, nullable=False, unique=True)

    class Author(db.Model):
        __tablename__ = 'authors'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Text, nullable=False)
        date_of_birth = db.Column(db.Date, nullable=False)
        date_of_death = db.Column(db.Date)

    class Book(db.Model):
        __tablename__ = 'books'
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(
            db.Integer,
            db.ForeignKey(Author.id),
            nullable=False
        )
        author = db.relationship(Author, backref='books')
        series_id = db.Column(db.Integer, db.ForeignKey(Series.id))
        series = db.relationship(Series, backref='books')
        date_published = db.Column(db.Date, nullable=False)
        title = db.Column(db.Text)

    class Chapter(db.Model):
        __tablename__ = 'chapters'
        id = db.Column(db.Integer, primary_key=True)
        book_id = db.Column(
            db.Integer,
            db.ForeignKey(Book.id, ondelete='CASCADE'),
            nullable=False,
        )
        title = db.Column(db.Text, nullable=False)
        ordering = db.Column(db.Integer, nullable=False)
        book = db.relationship(
            Book,
            backref=db.backref(
                'chapters',
                order_by=ordering,
                passive_deletes=True
            )
        )

    class Store(db.Model):
        __tablename__ = 'stores'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Text, nullable=False)
        books = db.relationship(Book, secondary=book_store, backref='stores')

    return Bunch(db.Model._decl_class_registry)


@pytest.fixture
def client(app):
    return app.test_client()


def build_attribute_serializer(schema_cls):
    def serialize(data):
        schema = schema_cls()
        result = schema.dump(data)
        return result.data
    return serialize


def build_attribute_deserializer(schema_cls):
    def deserialize(data):
        schema = schema_cls()
        result = schema.load(data)
        return result.data
    return deserialize
