import pytest
from flask_sqlalchemy import get_debug_queries

from flask_jsonapi import exc
from flask_jsonapi.params import Parameters
from flask_jsonapi.repository import SQLAlchemyRepository


class TestSQLAlchemyRepository(object):
    @pytest.fixture
    def repository(self, db):
        return SQLAlchemyRepository(db.session)

    def test_find_returns_all_models(
        self, resources, fantasy_database, repository, models
    ):
        params = Parameters(resources, 'books', {}, allow_include=True)
        books = repository.find(models.Book, params)
        assert len(books) == 11

    def test_find_loads_included_relations(
        self, fantasy_database, resources, repository, models
    ):
        params = Parameters(
            resources,
            'books',
            {'include': 'author.books,chapters'},
            allow_include=True
        )
        books = repository.find(models.Book, params)
        queries_before = len(get_debug_queries())
        for book in books:
            book.author.books
            book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_find_first_page(self, resources, fantasy_database, repository, models):
        params = Parameters(
            resources,
            'books',
            {'page': {'number': '1', 'size': '5'}},
            allow_pagination=True
        )
        books = repository.find(models.Book, params)
        assert len(books) == 5

    def test_find_last_page(self, resources, fantasy_database, repository, models):
        params = Parameters(
            resources,
            'books',
            {'page': {'number': '3', 'size': '5'}},
            allow_pagination=True
        )
        books = repository.find(models.Book, params)
        assert len(books) == 1

    def test_find_by_id_returns_requested_model(
        self, resources, fantasy_database, repository, models
    ):
        params = Parameters(resources, 'books', {})
        book = repository.find_by_id(models.Book, '11', params)
        assert isinstance(book, models.Book)
        assert book.id == 11

    def test_find_by_id_raises_error_if_model_not_found(
        self, resources, repository, models
    ):
        params = Parameters(resources, 'books', {})
        with pytest.raises(exc.ResourceNotFound) as exc_info:
            repository.find_by_id(models.Book, '123123', params)
        assert exc_info.value.id == '123123'

    def test_find_by_id_loads_included_relations(
        self, resources, repository, fantasy_database, models
    ):
        params = Parameters(
            resources,
            'books',
            {'include': 'author.books,chapters'},
            allow_include=True
        )
        book = repository.find_by_id(models.Book, '11', params)
        queries_before = len(get_debug_queries())
        book.author.books
        book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_find_count(self, fantasy_database, repository, models):
        count = repository.find_count(model_class=models.Book)
        assert count == 11

    def test_find_non_null_related_model(self, resources, fantasy_database, repository, models):
        params = Parameters(resources, 'authors', {})
        book = models.Book.query.get(11)
        author = repository.find_related_model(book, 'author', params)
        assert author.name == 'J. R. R. Tolkien'

    def test_find_related_model_loads_included_relations(self, resources, fantasy_database, repository, models):
        book = models.Book.query.get(11)
        params = Parameters(resources, 'authors', {'include': 'books'}, allow_include=True)
        author = repository.find_related_model(book, 'author', params)
        queries_before = len(get_debug_queries())
        author.books
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_find_null_related_model(self, resources, fantasy_database, repository, models):
        params = Parameters(resources, 'authors', {})
        book = models.Book.query.get(11)
        series = repository.find_related_model(book, 'series', params)
        assert series is None

    def test_validate_relationship_with_random_relationship_name(
        self, models, repository
    ):
        with pytest.raises(exc.InvalidRelationship) as exc_info:
            repository.validate_relationship(models.Book, 'foobar')
        assert str(exc_info.value) == (
            'foobar is not a valid relationship for Book.'
        )

    def test_validate_relationship_with_column_name(self, models, repository):
        with pytest.raises(exc.InvalidRelationship) as exc_info:
            repository.validate_relationship(models.Book, 'title')
        assert str(exc_info.value) == (
            'title is not a valid relationship for Book.'
        )

    def test_validate_relationship_with_to_many_relationship(
        self, models, repository
    ):
        repository.validate_relationship(models.Book, 'chapters')

    def test_validate_relationship_with_to_one_relationship(
        self, models, repository
    ):
        repository.validate_relationship(models.Book, 'author')
