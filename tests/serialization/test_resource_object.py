import pytest

from flask_jsonapi.serialization import resource_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


@pytest.mark.parametrize('fields,output', [
    (set(), {
        'type': 'books',
        'id': '1',
        'links': {
            'self': 'http://example.com/books/1'
        }
    }),
    ({'title', 'author', 'stores'}, {
        'type': 'books',
        'id': '1',
        'attributes': {
            'title': 'The Fellowship of the Ring'
        },
        'relationships': {
            'author': {
                'data': {'type': 'authors', 'id': '1'},
                'links': {
                    'self': 'http://example.com/books/1/relationships/author',
                    'related': 'http://example.com/books/1/author'
                }
            },
            'stores': {
                'links': {
                    'self': 'http://example.com/books/1/relationships/stores',
                    'related': 'http://example.com/books/1/stores'
                }
            }
        },
        'links': {
            'self': 'http://example.com/books/1'
        }
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert resource_object.dump(
        resource=resource,
        model=book,
        fields=fields
    ) == output
