import json
import os
from datetime import date, datetime

import pytest
from bunch import Bunch
from flask import Flask, Response
from flask.json import JSONEncoder as _JSONEncoder
from flask_sqlalchemy import SQLAlchemy

from flask_jsonapi import JSONAPI, ResourceRegistry
from flask_jsonapi.controller import PostgreSQLController
from flask_jsonapi.resource import Resource
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


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return JSONEncoder.default(self, o)


@pytest.yield_fixture
def app():
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgres://postgres@localhost/flask_json_api'
    )
    app.config['TESTING'] = True
    app.response_class = JSONResponse
    app.json_encoder = JSONEncoder
    with app.app_context():
        yield app


@pytest.fixture
def db(app):
    return SQLAlchemy(app)


@pytest.fixture(params=['default', 'postgresql'])
def jsonapi(app, request):
    if request.param == 'default':
        return JSONAPI(app)
    else:
        registry = ResourceRegistry()
        return JSONAPI(
            app,
            resource_registry=registry,
            controller=PostgreSQLController(registry)
        )


@pytest.fixture
def fantasy_database(db, models):
    with open(FANTASY_DATABASE_FILENAME, 'r') as f:
        data = json.loads(f.read())

    connection = db.engine.connect()
    table_names = [
        'stores',
        'authors',
        'series',
        'books',
        'chapters',
        'books_stores'
    ]
    for table_name in table_names:
        rows = data[table_name]
        table = db.metadata.tables[table_name]

        for row in rows:
            for column, value in row.items():
                if isinstance(table.columns[column].type, db.Date) and value:
                    row[column] = datetime.strptime(value, '%Y-%m-%d').date()

        connection.execute(table.insert(), rows)


@pytest.yield_fixture
def models(db):
    book_store = db.Table(
        'books_stores',
        db.Column(
            'book_id',
            db.Integer,
            db.ForeignKey('books.id'),
            nullable=False
        ),
        db.Column(
            'store_id',
            db.Integer,
            db.ForeignKey('stores.id'),
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

        @db.validates('date_of_birth')
        def validate_date_of_birth(self, key, date_of_birth):
            return datetime.strptime(date_of_birth, '%Y-%m-%d').date()

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

        @db.validates('date_published')
        def validate_date_published(self, key, date_published):
            return datetime.strptime(date_published, '%Y-%m-%d').date()

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

    db.create_all()

    yield Bunch(db.Model._decl_class_registry)

    table_names = [
        'stores',
        'authors',
        'series',
        'books',
        'chapters',
        'books_stores'
    ]
    for table_name in reversed(table_names):
        db.session.execute('DROP TABLE {0} CASCADE'.format(table_name))
    db.session.commit()
    # db.drop_all()


@pytest.fixture
def resources(jsonapi, db, models):
    series = Resource(
        type='series',
        model_class=models.Series,
        store=SQLAlchemyStore(db.session),
    )
    series.add_attribute('title')

    authors = Resource(
        type='authors',
        model_class=models.Author,
        store=SQLAlchemyStore(db.session),
    )
    authors.allow_client_generated_ids = True
    authors.add_attribute('name')
    authors.add_attribute('date_of_birth')
    authors.add_attribute('date_of_death')
    authors.add_relationship('books')

    books = Resource(
        type='books',
        model_class=models.Book,
        store=SQLAlchemyStore(db.session),
    )
    books.add_attribute('date_published')
    books.add_attribute('title')
    books.add_relationship('author')
    books.add_relationship(
        'chapters',
        allow_include=True,
        allow_full_replacement=True
    )
    books.add_relationship('series')
    books.add_relationship('stores', allow_full_replacement=True)

    chapters = Resource(
        type='chapters',
        model_class=models.Chapter,
        store=SQLAlchemyStore(db.session),
    )
    chapters.add_attribute('title')
    chapters.add_attribute('ordering')
    chapters.add_relationship('book')

    stores = Resource(
        type='stores',
        model_class=models.Store,
        store=SQLAlchemyStore(db.session),
    )
    stores.add_attribute('name')
    stores.add_relationship('books')

    jsonapi.resources.register(series)
    jsonapi.resources.register(authors)
    jsonapi.resources.register(books)
    jsonapi.resources.register(chapters)
    jsonapi.resources.register(stores)

    return jsonapi.resources


@pytest.fixture
def client(app, resources):
    return app.test_client()
