import pytest

from flask_jsonapi.serialization import relationships_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


@pytest.mark.parametrize('fields,output', [
    (set(), {}),
    ({'title'}, {}),
    ({'author'}, {
        'author': {
            'data': {'type': 'authors', 'id': '1'},
            'links': {
                'self': 'http://example.com/books/1/relationships/author',
                'related': 'http://example.com/books/1/author'
            }
        }
    }),
    (None, {
        'author': {
            'data': {'type': 'authors', 'id': '1'},
            'links': {
                'self': 'http://example.com/books/1/relationships/author',
                'related': 'http://example.com/books/1/author'
            }
        },
        'chapters': {
            'data': [
                {'type': 'chapters', 'id': '1'},
                {'type': 'chapters', 'id': '2'},
                {'type': 'chapters', 'id': '3'},
                {'type': 'chapters', 'id': '4'},
                {'type': 'chapters', 'id': '5'},
                {'type': 'chapters', 'id': '6'},
                {'type': 'chapters', 'id': '7'},
                {'type': 'chapters', 'id': '8'},
                {'type': 'chapters', 'id': '9'},
                {'type': 'chapters', 'id': '10'},
                {'type': 'chapters', 'id': '11'},
                {'type': 'chapters', 'id': '12'},
                {'type': 'chapters', 'id': '13'},
                {'type': 'chapters', 'id': '14'},
                {'type': 'chapters', 'id': '15'},
                {'type': 'chapters', 'id': '16'},
                {'type': 'chapters', 'id': '17'},
                {'type': 'chapters', 'id': '18'},
                {'type': 'chapters', 'id': '19'},
                {'type': 'chapters', 'id': '20'},
                {'type': 'chapters', 'id': '21'},
                {'type': 'chapters', 'id': '22'},
            ],
            'links': {
                'self': 'http://example.com/books/1/relationships/chapters',
                'related': 'http://example.com/books/1/chapters'
            }
        },
        'series': {
            'data': {'type': 'series', 'id': '1'},
            'links': {
                'self': 'http://example.com/books/1/relationships/series',
                'related': 'http://example.com/books/1/series'
            }
        },
        'stores': {
            'links': {
                'self': 'http://example.com/books/1/relationships/stores',
                'related': 'http://example.com/books/1/stores'
            }
        }
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert relationships_object.dump(
        resource=resource,
        model=book,
        fields=fields
    ) == output
