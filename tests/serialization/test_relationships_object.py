import pytest

from flask_jsonapi.errors import JSONAPIException
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


@pytest.mark.parametrize(
    'raw_data,error',
    [
        ([], '[] is not of type \'object\''),
        (
            {'foo': None},
            '"foo" is not a valid relationship for "books" resource'
        ),
        (
            {'foo': None, 'bar': None},
            '"bar", "foo" are not valid relationships for "books" resource'
        ),
        (
            {'stores': {'data': []}},
            'Full replacement of "stores" relationship is disallowed'
        ),
    ]
)
def test_load_invalid(resource_registry, raw_data, error):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        relationships_object.load(resource=resource, raw_data=raw_data)

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == error


def test_load(resource_registry, models, fantasy_database):
    resource = resource_registry.by_type['books']
    output = relationships_object.load(
        resource=resource,
        raw_data={
            'author': {
                'data': {'type': 'authors', 'id': '1'}
            },
            'chapters': {
                'data': [
                    {'type': 'chapters', 'id': '1'},
                    {'type': 'chapters', 'id': '2'},
                ]
            }
        }
    )

    author = models.Author.query.get(1)
    chapters = [
        models.Chapter.query.get(1),
        models.Chapter.query.get(2),
    ]
    assert len(output) == 2
    assert output['author'] is author
    assert output['chapters'] == chapters
