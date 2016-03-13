import pytest

from flask_jsonapi.serialization import relationship_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(11)


@pytest.mark.parametrize('relationship_name,output', [
    ('author', {
        'data': {'type': 'authors', 'id': '1'},
        'links': {
            'self': 'http://example.com/books/11/relationships/author',
            'related': 'http://example.com/books/11/author',
        }
    }),
    ('series', {
        'data': None,
        'links': {
            'self': 'http://example.com/books/11/relationships/series',
            'related': 'http://example.com/books/11/series',
        }
    }),
    ('chapters', {
        'data': [
            {'type': 'chapters', 'id': '271'},
            {'type': 'chapters', 'id': '272'},
            {'type': 'chapters', 'id': '273'},
            {'type': 'chapters', 'id': '274'},
            {'type': 'chapters', 'id': '275'},
            {'type': 'chapters', 'id': '276'},
            {'type': 'chapters', 'id': '277'},
            {'type': 'chapters', 'id': '278'},
            {'type': 'chapters', 'id': '279'},
            {'type': 'chapters', 'id': '280'},
            {'type': 'chapters', 'id': '281'},
            {'type': 'chapters', 'id': '282'},
            {'type': 'chapters', 'id': '283'},
            {'type': 'chapters', 'id': '284'},
            {'type': 'chapters', 'id': '285'},
            {'type': 'chapters', 'id': '286'},
            {'type': 'chapters', 'id': '287'},
            {'type': 'chapters', 'id': '288'},
            {'type': 'chapters', 'id': '289'},
        ],
        'links': {
            'self': 'http://example.com/books/11/relationships/chapters',
            'related': 'http://example.com/books/11/chapters',
        }
    }),
    ('stores', {
        'links': {
            'self': 'http://example.com/books/11/relationships/stores',
            'related': 'http://example.com/books/11/stores',
        }
    }),
])
def test_dump(resource_registry, book, relationship_name, output):
    resource = resource_registry.by_type['books']
    assert relationship_object.dump(
        relationship=resource.relationships[relationship_name],
        model=book
    ) == output
