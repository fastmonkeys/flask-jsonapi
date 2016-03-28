import pytest
from flask_sqlalchemy import get_debug_queries

from flask_jsonapi import exceptions
from flask_jsonapi.datastructures import Page
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


class TestSQLAlchemyRepository(object):
    @pytest.fixture
    def book_store(self, db, models, fantasy_database):
        return SQLAlchemyStore(db.session, model_class=models.Book)

    @pytest.fixture
    def store_store(self, db, models, fantasy_database):
        return SQLAlchemyStore(db.session, model_class=models.Store)

    def test_fetch_many_returns_first_page(self, book_store):
        page = Page(number=1, size=10)
        pagination = book_store.fetch_many(page=page)
        assert pagination.total == 11
        assert len(pagination.models) == 10

    def test_fetch_many_returns_last_page(self, book_store):
        page = Page(number=2, size=10)
        pagination = book_store.fetch_many(page=page)
        assert pagination.total == 11
        assert len(pagination.models) == 1

    def test_fetch_many_loads_included_relations(self, book_store):
        page = Page(number=1, size=10)
        pagination = book_store.fetch_many(
            page=page,
            include={
                'author': {
                    'books': {},
                },
                'chapters': {}
            }
        )
        books = pagination.models
        queries_before = len(get_debug_queries())
        for book in books:
            book.author.books
            book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_one_returns_requested_model(self, book_store, models):
        book = book_store.fetch_one('11')
        assert isinstance(book, models.Book)
        assert book.id == 11

    def test_fetch_one_raises_error_if_model_not_found(self, book_store):
        with pytest.raises(exceptions.ObjectNotFound):
            book_store.fetch_one('123123')

    def test_fetch_one_loads_included_relations(self, book_store):
        book = book_store.fetch_one(
            id='11',
            include={
                'author': {
                    'books': {},
                },
                'chapters': {}
            }
        )
        queries_before = len(get_debug_queries())
        book.author.books
        book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_one_related(self, book_store, models):
        book = models.Book.query.get(11)
        author = book_store.fetch_one_related(book, 'author')
        assert author.name == 'J. R. R. Tolkien'

    def test_fetch_one_related_with_included_relations(self, book_store, models):
        book = models.Book.query.get(11)
        author = book_store.fetch_one_related(book, 'author', include={'books': {}})
        queries_before = len(get_debug_queries())
        author.books
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_one_related_null_relation(self, book_store, models):
        book = models.Book.query.get(11)
        series = book_store.fetch_one_related(book, 'series')
        assert series is None

    def test_fetch_many_related(self, book_store, models):
        book = models.Book.query.get(11)
        pagination = book_store.fetch_many_related(book, 'chapters')
        assert len(pagination.models) == 19

    def test_fetch_many_related_with_included_relations(self, book_store, models):
        book = models.Book.query.get(1)
        pagination = book_store.fetch_many_related(
            model=book,
            relationship='stores',
            include={'books': {}}
        )
        queries_before = len(get_debug_queries())
        pagination.models[0].books
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_fetch_many_related_with_pagination(self, book_store, models):
        book = models.Book.query.get(1)
        pagination = book_store.fetch_many_related(
            model=book,
            relationship='chapters',
            page=Page(number=2, size=20)
        )
        assert len(pagination.models) == 2

    def test_fetch_related_empty_to_many_relation(self, store_store, models):
        store = models.Store.query.get(1)
        pagination = store_store.fetch_many_related(store, 'books')
        assert pagination.models == []
