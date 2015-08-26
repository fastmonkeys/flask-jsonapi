import json
import os
from datetime import date, datetime

import pytest
from flask import Flask, Response
from flask.json import JSONEncoder as _JSONEncoder
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string

from bunch import Bunch
from flask_jsonapi import JSONAPI
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
        'postgres://localhost/flask_json_api'
    )
    app.config['TESTING'] = True
    app.response_class = JSONResponse
    app.json_encoder = JSONEncoder
    with app.app_context():
        yield app


@pytest.fixture
def db(app):
    return SQLAlchemy(app)


@pytest.fixture
def resource_registry(jsonapi):
    return jsonapi.resources


@pytest.fixture
def controller_class():
    return 'flask_jsonapi.controllers.default.DefaultController'


@pytest.fixture
def jsonapi(app, controller_class, db, models):
    jsonapi = JSONAPI(
        app,
        controller_class=import_string(controller_class)
    )

    series = Resource(
        type='series',
        model_class=models.Series,
        store=SQLAlchemyStore(db.session),
    )
    series.add_attribute('title')
    series.add_relationship('books', allow_include=True)

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

    return jsonapi


@pytest.yield_fixture
def fantasy_database(db, models):
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
        if table.name != 'books_stores':
            connection.execute(
                'ALTER SEQUENCE {table}_id_seq RESTART WITH {num_rows}'.format(
                    table=table.name,
                    num_rows=len(rows) + 1
                )
            )

    yield

    for table in reversed(db.metadata.sorted_tables):
        db.session.execute('DROP TABLE {0} CASCADE'.format(table.name))
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

    return Bunch(db.Model._decl_class_registry)


@pytest.fixture
def client(app, jsonapi):
    return app.test_client()
