import pytest

from flask_jsonapi.serialization import resource_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


@pytest.mark.parametrize('fields,output', [
    (set(), {
        'type': 'books',
        'id': '1'
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
                'links': {}
            },
            'stores': {
                'links': {}
            }
        }
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert resource_object.dump(
        resource=resource,
        obj=book,
        fields=fields
    ) == output
