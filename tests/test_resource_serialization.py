import datetime

import pytest

from flask_jsonapi.resource_serializer import ResourceSerializer


@pytest.fixture
def book(db, models, fantasy_database):
    return db.session.query(models.Book).filter_by(id=1).one()


def test_single_resource(jsonapi, resources, book, db):
    serializer = ResourceSerializer(jsonapi.resource_registry)
    data = serializer.dump(resources.BookResource(db.session, book))
    assert data == {
        "data": {
            "type": "books",
            "id": "1",
            "links": {
                "self": "http://example.com/books/1"
            },
            "attributes": {
                "title": "The Fellowship of the Ring",
                "date_published": datetime.date(1954, 7, 29)
            },
            "relationships": {
                "author": {
                    "links": {
                        "self": 'http://example.com/books/1/relationships/author',
                        "related": 'http://example.com/books/1/author'
                    },
                    "data": {
                        "type": "author",
                        "id": "1"
                    }
                },
                "chapters": {
                    "links": {
                        "self": 'http://example.com/books/1/relationships/chapters',
                        "related": 'http://example.com/books/1/chapters'
                    }
                },
                "series": {
                    "links": {
                        "self": 'http://example.com/books/1/relationships/series',
                        "related": 'http://example.com/books/1/series'
                    },
                    "data": None
                }
            }
        }
    }
