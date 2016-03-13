import pytest

from flask_jsonapi.serialization import link_builder


@pytest.fixture
def resource(resource_registry):
    return resource_registry.by_type['books']


@pytest.fixture
def model(models, fantasy_database):
    return models.Book.query.get(1)


def test_resource_self_link(resource, model):
    assert link_builder.resource_self_link(
        resource=resource,
        model=model
    ) == 'http://example.com/books/1'


def test_relationship_self_link(resource, model):
    assert link_builder.relationship_self_link(
        relationship=resource.relationships['author'],
        model=model
    ) == 'http://example.com/books/1/relationships/author'


def test_relationship_related_link(resource, model):
    assert link_builder.relationship_related_link(
        relationship=resource.relationships['author'],
        model=model
    ) == 'http://example.com/books/1/author'
