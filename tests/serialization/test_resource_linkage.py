import pytest

from flask_jsonapi.errors import JSONAPIException
from flask_jsonapi.serialization import resource_linkage


@pytest.fixture
def book(models, fantasy_database):
    return models.Book.query.get(11)


@pytest.mark.parametrize('relationship_name,output', [
    ('author', {'type': 'authors', 'id': '1'}),
    ('series', None),
    ('chapters', [
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
    ]),
])
def test_dump(resource_registry, book, relationship_name, output):
    resource = resource_registry.by_type['books']
    assert resource_linkage.dump(
        relationship=resource.relationships[relationship_name],
        related=getattr(book, relationship_name)
    ) == output


def test_load_empty_to_one(resource_registry):
    resource = resource_registry.by_type['books']
    assert resource_linkage.load(
        relationship=resource.relationships['author'],
        raw_data=None
    ) is None


def test_load_to_one(resource_registry, fantasy_database, models):
    resource = resource_registry.by_type['books']
    author = models.Author.query.get(1)
    assert resource_linkage.load(
        relationship=resource.relationships['author'],
        raw_data={'type': 'authors', 'id': '1'}
    ) is author


def test_load_to_many(resource_registry, fantasy_database, models):
    resource = resource_registry.by_type['books']
    chapters = [
        models.Chapter.query.get(1),
        models.Chapter.query.get(2),
    ]
    assert resource_linkage.load(
        relationship=resource.relationships['chapters'],
        raw_data=[
            {'type': 'chapters', 'id': '1'},
            {'type': 'chapters', 'id': '2'},
        ]
    ) == chapters


def test_load_invalid(resource_registry, fantasy_database, models):
    resource = resource_registry.by_type['books']
    with pytest.raises(JSONAPIException) as excinfo:
        resource_linkage.load(
            relationship=resource.relationships['chapters'],
            raw_data=[
                {'type': 'chapters', 'id': '1'},
                {'type': 'chapters'},
            ]
        )

    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].detail == '"id" is a required property'
    assert errors[0].source_pointer == '/1'
