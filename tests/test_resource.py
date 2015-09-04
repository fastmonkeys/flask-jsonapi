import pytest

from flask_jsonapi import exceptions
from flask_jsonapi.paginator import OffsetPaginator, PagedPaginator
from flask_jsonapi.resource import Attribute, Field, Relationship, Resource
from flask_jsonapi.resource_registry import ResourceRegistry
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


class TestResource(object):
    @pytest.fixture
    def make_resource(self, db, models):
        return lambda **kwargs: Resource(
            type='books',
            model_class=models.Book,
            store=SQLAlchemyStore(db.session),
            fields=kwargs.pop('fields', []),
            **kwargs
        )

    def test_allow_client_generated_ids_defaults_to_false(self, make_resource):
        resource = make_resource()
        assert resource.allow_client_generated_ids is False

    def test_can_override_allow_client_generated_ids(self, make_resource):
        resource = make_resource(allow_client_generated_ids=True)
        assert resource.allow_client_generated_ids is True

    def test_paginator_defaults_to_paged(self, make_resource):
        resource = make_resource()
        assert isinstance(resource.paginator, PagedPaginator)

    def test_can_override_paginator(self, make_resource):
        paginator = OffsetPaginator()
        resource = make_resource(paginator=paginator)
        assert resource.paginator is paginator

    def test_attribute_is_classified_correctly(self, make_resource):
        resource = make_resource(fields=[Attribute('title')])
        assert 'title' in resource.fields
        assert 'title' in resource.attributes
        assert len(resource.relationships) == 0
        assert isinstance(resource.attributes['title'], Attribute)
        assert resource.fields['title'] is resource.attributes['title']

    def test_relationship_is_classified_correctly(self, make_resource, models):
        resource = make_resource(fields=[Relationship('chapters')])
        assert 'chapters' in resource.fields
        assert 'chapters' in resource.relationships
        assert len(resource.attributes) == 0
        assert isinstance(resource.relationships['chapters'], Relationship)
        assert (
            resource.fields['chapters'] is
            resource.relationships['chapters']
        )

    def test_validated_field_is_of_correct_type(self, make_resource):
        with pytest.raises(TypeError) as excinfo:
            make_resource(fields=['foobar'])
        assert str(excinfo.value) == "expected Field"

    def test_cannot_add_field_with_same_name_twice(self, make_resource):
        with pytest.raises(exceptions.FieldNamingConflict) as excinfo:
            make_resource(fields=[
                Attribute('title'),
                Attribute('title')
            ])
        assert str(excinfo.value) == (
            "The resource already has a field called 'title'."
        )

    def test_cannot_register_twice(self, make_resource):
        resource = make_resource()
        registry1 = ResourceRegistry()
        registry2 = ResourceRegistry()
        registry1.register(resource)
        with pytest.raises(exceptions.ResourceAlreadyRegistered) as excinfo:
            registry2.register(resource)
        assert str(excinfo.value) == (
            "<Resource type='books'> has already been registered."
        )

    def test___repr__(self, make_resource):
        resource = make_resource()
        assert repr(resource) == "<Resource type='books'>"


class TestField(object):
    @pytest.mark.parametrize('name', ['id', 'type'])
    def test_cannot_have_invalid_name(self, name):
        with pytest.raises(exceptions.FieldNamingConflict) as exc_info:
            Field(name=name)
        assert str(exc_info.value) == (
            "A resource cannot have a field named 'type' or 'id'."
        )

    def test_validators_defaults_to_noop(self):
        field = Field(name='title')
        assert field.validator('foobar') == 'foobar'


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
