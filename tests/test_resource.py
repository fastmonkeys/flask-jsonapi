import pytest

from flask_jsonapi import Resource, fields
# from flask_jsonapi import exceptions
from flask_jsonapi.paginator import OffsetPaginator, PagedPaginator


# from flask_jsonapi.resource_registry import ResourceRegistry
# from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


# id must be a string
# cannot have a field called type
# store is required

class TestResource(object):
    # @pytest.fixture
    # def make_resource(self, db, models):
    #     return lambda **kwargs: Resource(
    #         type='books',
    #         model_class=models.Book,
    #         store=SQLAlchemyStore(db.session),
    #         fields=kwargs.pop('fields', []),
    #         **kwargs
    #     )

    def test_id_is_required(self):
        class BookResource(Resource):
            class Meta:
                type_ = 'books'

        with pytest.raises(ValueError) as excinfo:
            BookResource()

        assert str(excinfo.value) == '`id` field is required.'

    def test_type_is_required(self):
        class BookResource(Resource):
            id = fields.Str()

        with pytest.raises(ValueError) as excinfo:
            BookResource()

        assert str(excinfo.value) == '`type_` option must be specified.'

    def test_allow_client_generated_ids_defaults_to_false(self):
        class BookResource(Resource):
            id = fields.Str()

            class Meta:
                type_ = 'books'

        resource = BookResource()
        assert resource.opts.allow_client_generated_ids is False

    def test_can_override_allow_client_generated_ids(self):
        class BookResource(Resource):
            id = fields.Str()

            class Meta:
                type_ = 'books'
                allow_client_generated_ids = True

        resource = BookResource()
        assert resource.opts.allow_client_generated_ids is True

    def test_paginator_defaults_to_none(self):
        class BookResource(Resource):
            id = fields.Str()

            class Meta:
                type_ = 'books'

        resource = BookResource()
        assert resource.opts.paginator is None

    def test_can_override_paginator(self):
        class BookResource(Resource):
            id = fields.Str()

            class Meta:
                type_ = 'books'
                paginator = OffsetPaginator()

        resource = BookResource()
        assert isinstance(resource.opts.paginator, OffsetPaginator)
#
#     def test_attribute_is_classified_correctly(self, make_resource):
#         resource = make_resource(fields=[Attribute('title')])
#         assert 'title' in resource.fields
#         assert 'title' in resource.attributes
#         assert len(resource.relationships) == 0
#         assert isinstance(resource.attributes['title'], Attribute)
#         assert resource.fields['title'] is resource.attributes['title']
#
#     def test_relationship_is_classified_correctly(self, make_resource, models):
#         resource = make_resource(fields=[Relationship('chapters')])
#         assert 'chapters' in resource.fields
#         assert 'chapters' in resource.relationships
#         assert len(resource.attributes) == 0
#         assert isinstance(resource.relationships['chapters'], Relationship)
#         assert (
#             resource.fields['chapters'] is
#             resource.relationships['chapters']
#         )

#     def test_cannot_register_twice(self, make_resource):
#         resource = make_resource()
#         registry1 = ResourceRegistry()
#         registry2 = ResourceRegistry()
#         registry1.register(resource)
#         with pytest.raises(exceptions.ResourceAlreadyRegistered) as excinfo:
#             registry2.register(resource)
#         assert str(excinfo.value) == (
#             "<Resource type='books'> has already been registered."
#         )
#
#     def test___repr__(self, make_resource):
#         resource = make_resource()
#         assert repr(resource) == "<Resource type='books'>"
#
#
    def test_cannot_have_field_called_type(self):
        class BookResource(Resource):
            id = fields.Str()
            type = fields.Str()

            class Meta:
                type_ = 'books'

        with pytest.raises(ValueError) as exc_info:
            BookResource()

        assert str(exc_info.value) == 'Cannot have a field called `type`.'
#
#
# class TestRelationship(object):
#     @pytest.fixture
#     def authors(self, resource_registry):
#         return resource_registry.by_type['authors']
#
#     @pytest.fixture
#     def books(self, resource_registry):
#         return resource_registry.by_type['books']
#
#     @pytest.fixture
#     def books_author(self, books):
#         return books.relationships['author']
#
#     @pytest.fixture
#     def books_chapters(self, books):
#         return books.relationships['chapters']
#
#     @pytest.fixture
#     def authors_books(self, authors):
#         return authors.relationships['books']
#
#     def test_to_one_relationship_is_recognized(self, books_author):
#         assert books_author.many is False
#
#     def test_to_one_relationship_defaults(self, books_author):
#         assert books_author.allow_include is True
#
#     def test_to_many_relationship_is_recognized(self, books_chapters):
#         assert books_chapters.many is True
#
#     def test_to_many_relationship_defaults(self, authors_books):
#         assert authors_books.allow_include is False
#         assert authors_books.allow_full_replacement is False
#
#     def test_can_override_relationship_defaults(self, books_chapters):
#         assert books_chapters.allow_include is True
#         assert books_chapters.allow_full_replacement is True
#
#     def test_model_class(self, books_author, models):
#         assert books_author.model_class is models.Author
#
#     def test_resource(self, books_author, authors):
#         assert books_author.resource is authors
#
#     def test_type(self, books_author):
#         assert books_author.type == 'authors'
#
#     def test___repr__(self, resource_registry):
#         authors = resource_registry.by_type['authors']
#         relationship = authors.relationships['books']
#         assert repr(relationship) == "<Relationship name='books'>"
