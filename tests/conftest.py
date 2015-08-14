import json
import os
from datetime import date, datetime

import pytest
from bunch import Bunch
from flask import Flask, Response
from flask.json import JSONEncoder as _JSONEncoder
from flask_sqlalchemy import SQLAlchemy

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
    app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
    app.config['TESTING'] = True
    app.response_class = JSONResponse
    app.json_encoder = JSONEncoder
    with app.app_context():
        yield app


@pytest.fixture
def db(app):
    return SQLAlchemy(app)


@pytest.fixture
def jsonapi(app):
    return JSONAPI(app)


@pytest.fixture
def fantasy_database(db, models):
    with open(FANTASY_DATABASE_FILENAME, 'r') as f:
        data = json.loads(f.read())

    connection = db.engine.connect()
    for table_name, rows in data.items():
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

    db.drop_all()


@pytest.fixture
def resources(jsonapi, db, models):
    jsonapi.resources.register(
        Resource(
            type='series',
            model_class=models.Series,
            store=SQLAlchemyStore(db.session),
            attributes=('title',)
        )
    )
    jsonapi.resources.register(
        Resource(
            type='authors',
            model_class=models.Author,
            store=SQLAlchemyStore(db.session),
            attributes=('name', 'date_of_birth', 'date_of_death'),
            relationships=('books',),
            allow_client_generated_ids=True
        )
    )
    jsonapi.resources.register(
        Resource(
            type='books',
            model_class=models.Book,
            store=SQLAlchemyStore(db.session),
            attributes=('date_published', 'title'),
            relationships=('author', 'chapters', 'series', 'stores')
        )
    )
    jsonapi.resources.register(
        Resource(
            type='chapters',
            model_class=models.Chapter,
            store=SQLAlchemyStore(db.session),
            attributes=('title', 'ordering'),
            relationships=('book',)
        )
    )
    jsonapi.resources.register(
        Resource(
            type='stores',
            model_class=models.Store,
            store=SQLAlchemyStore(db.session),
            attributes=('name',),
            relationships=('books',)
        )
    )
    return jsonapi.resources


@pytest.fixture
def client(app, resources):
    return app.test_client()
