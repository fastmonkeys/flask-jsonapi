import datetime

import pytest

from flask_jsonapi.errors import JSONAPIException
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
        'date_published': '1954-07-29'
    }),
])
def test_dump(resource_registry, book, fields, output):
    resource = resource_registry.by_type['books']
    assert attributes_object.dump(
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
            '"foo" is not a valid attribute for "books" resource'
        ),
        (
            {'foo': None, 'bar': None},
            '"bar", "foo" are not valid attributes for "books" resource'
        ),
    ]
)
def test_load_invalid(resource_registry, raw_data, error):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        attributes_object.load(
            resource=resource,
            raw_data=raw_data
        )

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == error


def test_load(resource_registry, models, fantasy_database):
    resource = resource_registry.by_type['books']
    output = attributes_object.load(
        resource=resource,
        raw_data={
            'title': 'The Hobbit',
            'date_published': '1937-09-21',
        }
    )

    assert len(output) == 2
    assert output['title'] == 'The Hobbit'
    assert output['date_published'] == datetime.date(1937, 9, 21)
