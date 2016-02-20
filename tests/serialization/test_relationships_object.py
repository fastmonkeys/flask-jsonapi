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
            'links': {}
        }
    }),
    (None, {
        'author': {
            'data': {'type': 'authors', 'id': '1'},
            'links': {}
        },
        'series': {
            'links': {}
        },
        'stores': {
            'links': {}
        }
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert relationships_object.dump(
        resource=resource,
        obj=book,
        fields=fields
    ) == output
