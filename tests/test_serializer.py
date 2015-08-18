import datetime

import pytest

from flask_jsonapi.params import Parameters
from flask_jsonapi.serializer import Serializer


@pytest.fixture
def books(db, models, fantasy_database):
    return db.session.query(models.Book).all()


@pytest.fixture
def book(db, models, fantasy_database):
    return db.session.query(models.Book).filter_by(id=11).one()


@pytest.fixture
def author(db, models, fantasy_database):
    return db.session.query(models.Author).filter_by(id=1).one()


def test_single_resource(jsonapi, resource_registry, book, db):
    params = Parameters(
        resource_registry=resource_registry,
        type='books',
        params={}
    )
    serializer = Serializer(resource_registry=resource_registry, params=params)
    data = serializer.dump(book)
    assert data == {
        "data": {
            "type": "books",
            "id": "11",
            "links": {
                "self": "http://example.com/books/11"
            },
            "attributes": {
                "title": "The Hobbit",
                "date_published": datetime.date(1937, 9, 21)
            },
            "relationships": {
                "author": {
                    "links": {
                        "self": (
                            "http://example.com/books/11/relationships/author"
                        ),
                        "related": "http://example.com/books/11/author"
                    },
                    "data": {
                        "type": "authors",
                        "id": "1"
                    }
                },
                "chapters": {
                    "links": {
                        "self": (
                            "http://example.com/books/11/relationships"
                            "/chapters"
                        ),
                        "related": "http://example.com/books/11/chapters"
                    },
                    "data": [
                        {"id": "271", "type": "chapters"},
                        {"id": "272", "type": "chapters"},
                        {"id": "273", "type": "chapters"},
                        {"id": "274", "type": "chapters"},
                        {"id": "275", "type": "chapters"},
                        {"id": "276", "type": "chapters"},
                        {"id": "277", "type": "chapters"},
                        {"id": "278", "type": "chapters"},
                        {"id": "279", "type": "chapters"},
                        {"id": "280", "type": "chapters"},
                        {"id": "281", "type": "chapters"},
                        {"id": "282", "type": "chapters"},
                        {"id": "283", "type": "chapters"},
                        {"id": "284", "type": "chapters"},
                        {"id": "285", "type": "chapters"},
                        {"id": "286", "type": "chapters"},
                        {"id": "287", "type": "chapters"},
                        {"id": "288", "type": "chapters"},
                        {"id": "289", "type": "chapters"},
                    ]
                },
                "series": {
                    "links": {
                        "self": (
                            "http://example.com/books/11/relationships/series"
                        ),
                        "related": "http://example.com/books/11/series"
                    },
                    "data": None
                },
                "stores": {
                    "links": {
                        "self": (
                            "http://example.com/books/11/relationships/stores"
                        ),
                        "related": "http://example.com/books/11/stores"
                    },
                    "data": [
                        {"type": "stores", "id": "2"}
                    ]
                }
            }
        }
    }


def test_null_resource(jsonapi, resource_registry, db):
    params = Parameters(
        resource_registry=resource_registry,
        type='books',
        params={}
    )
    serializer = Serializer(resource_registry=resource_registry, params=params)
    data = serializer.dump(None)
    assert data == {
        "data": None
    }


def test_sparse_fieldsets(jsonapi, resource_registry, book, db):
    params = Parameters(
        resource_registry=resource_registry,
        type='books',
        params={
            'fields': {'books': 'title,author'}
        }
    )
    serializer = Serializer(
        resource_registry=resource_registry,
        params=params,
    )
    data = serializer.dump(book)
    assert data == {
        "data": {
            "type": "books",
            "id": "11",
            "links": {
                "self": "http://example.com/books/11"
            },
            "attributes": {
                "title": "The Hobbit",
            },
            "relationships": {
                "author": {
                    "links": {
                        "self": (
                            "http://example.com/books/11/relationships/author"
                        ),
                        "related": "http://example.com/books/11/author"
                    },
                    "data": {
                        "type": "authors",
                        "id": "1"
                    }
                },
            }
        }
    }


def test_inclusion_of_related_resources(
    jsonapi, resource_registry, author, db
):
    params = Parameters(
        resource_registry=resource_registry,
        type='authors',
        params={
            'fields': {
                'authors': 'name,books',
                'books': 'title',
                'series': 'title'
            },
            'include': 'books,books.series'
        }
    )
    serializer = Serializer(resource_registry=resource_registry, params=params)
    data = serializer.dump(author)
    assert len(data['included']) == 5
    assert data == {
        "data": {
            "id": "1",
            "type": "authors",
            "attributes": {
                "name": "J. R. R. Tolkien"
            },
            "relationships": {
                "books": {
                    "data": [
                        {"id": "1", "type": "books"},
                        {"id": "2", "type": "books"},
                        {"id": "3", "type": "books"},
                        {"id": "11", "type": "books"}
                    ],
                    "links": {
                        "related": "http://example.com/authors/1/books",
                        "self": (
                            "http://example.com/authors/1/relationships/books"
                        )
                    }
                }
            },
            "links": {
                "self": "http://example.com/authors/1"
            },
        },
        "included": [
            {
                "id": "1",
                "type": "books",
                "attributes": {
                    "title": "The Fellowship of the Ring"
                },
                "links": {
                    "self": "http://example.com/books/1"
                },
            },
            {
                "id": "1",
                "type": "series",
                "attributes": {
                    "title": "The Lord of the Rings"
                },
                "links": {
                    "self": "http://example.com/series/1"
                },
            },
            {
                "id": "2",
                "type": "books",
                "attributes": {
                    "title": "The Two Towers"
                },
                "links": {
                    "self": "http://example.com/books/2"
                },
            },
            {
                "id": "3",
                "type": "books",
                "attributes": {
                    "title": "Return of the King"
                },
                "links": {
                    "self": "http://example.com/books/3"
                },
            },
            {
                "id": "11",
                "type": "books",
                "attributes": {
                    "title": "The Hobbit"
                },
                "links": {
                    "self": "http://example.com/books/11"
                },
            },
        ]
    }


def test_resource_collection(jsonapi, resource_registry, books, db):
    params = Parameters(
        resource_registry=resource_registry,
        type='books',
        params={}
    )
    serializer = Serializer(resource_registry=resource_registry, params=params)
    data = serializer.dump(books)
    assert len(data['data']) == 11
