import pytest
from flask_sqlalchemy import get_debug_queries

from flask_jsonapi import exceptions
from flask_jsonapi.params import Parameters
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


class TestSQLAlchemyRepository(object):
    @pytest.fixture
    def store(self, db):
        return SQLAlchemyStore(db.session)

    def test_fetch_returns_all_models(
        self, resource_registry, fantasy_database, store, models
    ):
        params = Parameters(resource_registry, 'books', {})
        books = store.fetch(models.Book, params)
        assert len(books) == 11

    def test_fetch_loads_included_relations(
        self, fantasy_database, resource_registry, store, models
    ):
        params = Parameters(
            resource_registry,
            'books',
            {'include': 'author.books,chapters'}
        )
        books = store.fetch(models.Book, params)
        queries_before = len(get_debug_queries())
        for book in books:
            book.author.books
            book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_first_page(self, resource_registry, fantasy_database, store, models):
        params = Parameters(
            resource_registry,
            'books',
            {'page': {'number': '1', 'size': '5'}}
        )
        books = store.fetch(models.Book, params)
        assert len(books) == 5

    def test_fetch_last_page(self, resource_registry, fantasy_database, store, models):
        params = Parameters(
            resource_registry,
            'books',
            {'page': {'number': '3', 'size': '5'}}
        )
        books = store.fetch(models.Book, params)
        assert len(books) == 1

    def test_fetch_one_returns_requested_model(
        self, resource_registry, fantasy_database, store, models
    ):
        params = Parameters(resource_registry, 'books', {})
        book = store.fetch_one(models.Book, '11', params)
        assert isinstance(book, models.Book)
        assert book.id == 11

    def test_fetch_one_raises_error_if_model_not_found(
        self, resource_registry, fantasy_database, store, models
    ):
        params = Parameters(resource_registry, 'books', {})
        with pytest.raises(exceptions.ObjectNotFound):
            store.fetch_one(models.Book, '123123', params)

    def test_fetch_one_loads_included_relations(
        self, resource_registry, store, fantasy_database, models
    ):
        params = Parameters(
            resource_registry,
            'books',
            {'include': 'author.books,chapters'}
        )
        book = store.fetch_one(models.Book, '11', params)
        queries_before = len(get_debug_queries())
        book.author.books
        book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_count(self, fantasy_database, store, models):
        count = store.count(model_class=models.Book)
        assert count == 11

    def test_fetch_related_to_one_relation(self, resource_registry, fantasy_database, store, models):
        params = Parameters(resource_registry, 'authors', {})
        book = models.Book.query.get(11)
        author = store.fetch_related(book, 'author', params)
        assert author.name == 'J. R. R. Tolkien'

    def test_fetch_related_to_one_relation_with_included_relations(self, resource_registry, fantasy_database, store, models):
        book = models.Book.query.get(11)
        params = Parameters(resource_registry, 'authors', {'include': 'books'})
        author = store.fetch_related(book, 'author', params)
        queries_before = len(get_debug_queries())
        author.books
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_related_null_to_one_relation(self, resource_registry, fantasy_database, store, models):
        params = Parameters(resource_registry, 'authors', {})
        book = models.Book.query.get(11)
        series = store.fetch_related(book, 'series', params)
        assert series is None

    def test_fetch_related_to_many_relation(self, resource_registry, fantasy_database, store, models):
        params = Parameters(resource_registry, 'books', {})
        author = models.Author.query.get(1)
        books = store.fetch_related(author, 'books', params)
        assert len(books) == 4

    def test_fetch_related_to_many_relation_with_included_relations(self, resource_registry, fantasy_database, store, models):
        params = Parameters(resource_registry, 'books', {'include': 'chapters'})
        author = models.Author.query.get(1)
        books = store.fetch_related(author, 'books', params)
        queries_before = len(get_debug_queries())
        books[0].chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_related_to_many_relation_with_pagination(self, resource_registry, fantasy_database, store, models):
        params = Parameters(
            resource_registry,
            'chapters',
            {'page': {'number': '2', 'size': '20'}}
        )
        book = models.Book.query.get(1)
        chapters = store.fetch_related(book, 'chapters', params)
        assert len(chapters) == 2

    def test_fetch_related_empty_to_many_relation(self, resource_registry, fantasy_database, store, models):
        params = Parameters(resource_registry, 'books', {})
        book_store = models.Store.query.get(1)
        books = store.fetch_related(book_store, 'books', params)
        assert books == []

    def test_validate_relationship_with_random_relationship_name(
        self, models, store
    ):
        with pytest.raises(exceptions.InvalidRelationship) as exc_info:
            store.validate_relationship(models.Book, 'foobar')
        assert str(exc_info.value) == (
            'foobar is not a valid relationship for Book.'
        )

    def test_validate_relationship_with_column_name(self, models, store):
        with pytest.raises(exceptions.InvalidRelationship) as exc_info:
            store.validate_relationship(models.Book, 'title')
        assert str(exc_info.value) == (
            'title is not a valid relationship for Book.'
        )

    def test_validate_relationship_with_to_many_relationship(
        self, models, store
    ):
        store.validate_relationship(models.Book, 'chapters')

    def test_validate_relationship_with_to_one_relationship(
        self, models, store
    ):
        store.validate_relationship(models.Book, 'author')
