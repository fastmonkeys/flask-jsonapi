import pytest

from flask_jsonapi.serialization import resource_identifier


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


def test_dump(resource_registry, book):
    resource = resource_registry.by_type['books']
    assert resource_identifier.dump(resource=resource, model=book) == {
        'type': 'books',
        'id': '1'
    }
