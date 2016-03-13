import pytest
import datetime

from flask_jsonapi.serialization import attributes_object


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(1)


@pytest.mark.parametrize('fields,output', [
    (set(), {}),
    ({'title'}, {'title': 'The Fellowship of the Ring'}),
    ({'author'}, {}),
    (None, {
        'title': 'The Fellowship of the Ring',
        'date_published': datetime.date(1954, 7, 29)
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert attributes_object.dump(
        resource=resource,
        model=book,
        fields=fields
    ) == output
