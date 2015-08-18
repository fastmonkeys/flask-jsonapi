import pytest

from flask_jsonapi import exceptions
from flask_jsonapi.paginator import PagedPaginator
from flask_jsonapi.resource import Attribute, Relationship, Resource
from flask_jsonapi.resource_registry import ResourceRegistry
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


class TestResource(object):
    @pytest.fixture
    def resource(self, db, models):
        return Resource(
            type='books',
            model_class=models.Book,
            store=SQLAlchemyStore(db.session)
        )

    def test_allow_client_generated_ids_defaults_to_false(self, resource):
        assert resource.allow_client_generated_ids is False

    def test_paginator_defaults_to_paged(self, resource):
        assert isinstance(resource.paginator, PagedPaginator)

    @pytest.mark.parametrize('attr', ['id', 'type'])
    def test_cannot_have_invalid_attribute_names(self, resource, attr):
        with pytest.raises(exceptions.FieldNamingConflict) as exc_info:
            resource.add_attribute(attr)

        assert str(exc_info.value) == (
            "A resource cannot have a field named 'type' or 'id'."
        )

    @pytest.mark.parametrize('attr', ['id', 'type'])
    def test_cannot_have_invalid_relationship_names(self, resource, attr):
        with pytest.raises(exceptions.FieldNamingConflict) as exc_info:
            resource.add_relationship(attr)

        assert str(exc_info.value) == (
            "A resource cannot have a field named 'type' or 'id'."
        )

    def test_add_attribute(self, resource):
        resource.add_attribute('title')
        assert 'title' in resource.fields
        assert 'title' in resource.attributes
        assert isinstance(resource.attributes['title'], Attribute)
        assert resource.fields['title'] is resource.attributes['title']

    def test_add_relationship(self, resource, models):
        resource.add_relationship('chapters')
        assert 'chapters' in resource.fields
        assert 'chapters' in resource.relationships
        assert isinstance(resource.relationships['chapters'], Relationship)
        assert (
            resource.fields['chapters'] is
            resource.relationships['chapters']
        )

    def test_cannot_add_field_with_same_name_twice(self, resource):
        resource.add_attribute('title')
        with pytest.raises(exceptions.FieldNamingConflict) as excinfo:
            resource.add_attribute('title')
        assert str(excinfo.value) == (
            "The resource already has a field called 'title'."
        )

    def test_cannot_register_twice(self, resource):
        registry1 = ResourceRegistry()
        registry2 = ResourceRegistry()
        registry1.register(resource)
        with pytest.raises(exceptions.ResourceAlreadyRegistered) as excinfo:
            registry2.register(resource)
        assert str(excinfo.value) == (
            "<Resource type='books'> has already been registered."
        )

    def test___repr__(self, resource):
        assert repr(resource) == "<Resource type='books'>"


class TestAttribute(object):
    def test___repr__(self, resource_registry):
        books = resource_registry.by_type['books']
        assert repr(books.attributes['title']) == "<Attribute name='title'>"


class TestRelationship(object):
    @pytest.fixture
    def authors(self, resource_registry):
        return resource_registry.by_type['authors']

    @pytest.fixture
    def books(self, resource_registry):
        return resource_registry.by_type['books']

    @pytest.fixture
    def books_author(self, books):
        return books.relationships['author']

    @pytest.fixture
    def books_chapters(self, books):
        return books.relationships['chapters']

    @pytest.fixture
    def authors_books(self, authors):
        return authors.relationships['books']

    def test_to_one_relationship_is_recognized(self, books_author):
        assert books_author.many is False

    def test_to_one_relationship_defaults(self, books_author):
        assert books_author.allow_include is True

    def test_to_many_relationship_is_recognized(self, books_chapters):
        assert books_chapters.many is True

    def test_to_many_relationship_defaults(self, authors_books):
        assert authors_books.allow_include is False
        assert authors_books.allow_full_replacement is False

    def test_can_override_relationship_defaults(self, books_chapters):
        assert books_chapters.allow_include is True
        assert books_chapters.allow_full_replacement is True

    def test_model_class(self, books_author, models):
        assert books_author.model_class is models.Author

    def test_resource(self, books_author, authors):
        assert books_author.resource is authors

    def test_type(self, books_author):
        assert books_author.type == 'authors'

    def test___repr__(self, resource_registry):
        authors = resource_registry.by_type['authors']
        relationship = authors.relationships['books']
        assert repr(relationship) == "<Relationship name='books'>"
