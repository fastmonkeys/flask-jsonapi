
import json
import os
from datetime import datetime

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from bunch import Bunch
from flask_jsonapi import JSONAPI
from flask_jsonapi.repository import SQLAlchemyRepository
from flask_jsonapi.resource import Resource

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FANTASY_DATABASE_FILENAME = os.path.join(
    PROJECT_ROOT,
    'node_modules',
    'fantasy-database',
    'data.json'
)


@pytest.yield_fixture
def app():
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'example.com'
    app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
    app.config['TESTING'] = True
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

    class Book(db.Model):
        __tablename__ = 'books'
        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(
            db.Integer,
            db.ForeignKey(Author.id),
            nullable=False
        )
        author = db.relationship(Author)
        series_id = db.Column(db.Integer, db.ForeignKey(Series.id))
        series = db.relationship(Series)
        date_published = db.Column(db.Date, nullable=False)
        title = db.Column(db.Text)

    class Chapter(db.Model):
        __tablename__ = 'chapters'
        id = db.Column(db.Integer, primary_key=True)
        book_id = db.Column(db.Integer, db.ForeignKey(Book.id), nullable=False)
        book = db.relationship(Book)
        title = db.Column(db.Text, nullable=False)
        ordering = db.Column(db.Integer, nullable=False)

    class Store(db.Model):
        __tablename__ = 'stores'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.Text, nullable=False)
        books = db.relationship(Book, secondary=book_store)

    db.create_all()

    yield Bunch(db.Model._decl_class_registry)

    db.drop_all()


@pytest.fixture
def resources(jsonapi, db, models):
    jsonapi.resources.register(
        Resource(
            type='series',
            model_class=models.Series,
            repository=SQLAlchemyRepository(db.session),
            attributes=('title',)
        )
    )
    jsonapi.resources.register(
        Resource(
            type='authors',
            model_class=models.Author,
            repository=SQLAlchemyRepository(db.session),
            attributes=('name', 'date_of_birth', 'date_of_death')
        )
    )
    jsonapi.resources.register(
        Resource(
            type='books',
            model_class=models.Book,
            repository=SQLAlchemyRepository(db.session),
            attributes=('date_published', 'title'),
            relationships=('author', 'series')
        )
    )
    jsonapi.resources.register(
        Resource(
            type='chapters',
            model_class=models.Chapter,
            repository=SQLAlchemyRepository(db.session),
            attributes=('title', 'ordering'),
            relationships=('book',)
        )
    )
    jsonapi.resources.register(
        Resource(
            type='stores',
            model_class=models.Store,
            repository=SQLAlchemyRepository(db.session),
            attributes=('name',),
            relationships=('books',)
        )
    )
    return jsonapi.resources
