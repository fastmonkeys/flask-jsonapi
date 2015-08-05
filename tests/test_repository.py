import pytest
from flask_sqlalchemy import get_debug_queries

from flask_jsonapi import exc
from flask_jsonapi.paginator import PagedPagination
from flask_jsonapi.params import IncludeParameter
from flask_jsonapi.repository import SQLAlchemyRepository


class TestSQLAlchemyRepository(object):
    @pytest.fixture
    def repository(self, db):
        return SQLAlchemyRepository(db.session)

    def test_find_returns_all_models(
        self, fantasy_database, repository, models
    ):
        books = repository.find(models.Book)
        assert len(books) == 11

    def test_find_loads_included_relations(
        self, fantasy_database, resources, repository, models
    ):
        include = IncludeParameter(
            resources,
            type='books',
            include='author.books,chapters'
        )
        books = repository.find(models.Book, include=include)
        queries_before = len(get_debug_queries())
        for book in books:
            book.author.books
            book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_find_first_page(self, fantasy_database, repository, models):
        books = repository.find(
            models.Book,
            pagination=PagedPagination(
                number=1,
                size=5,
                total=repository.find_count(models.Book)
            )
        )
        assert len(books) == 5

    def test_find_last_page(self, fantasy_database, repository, models):
        books = repository.find(
            models.Book,
            pagination=PagedPagination(
                number=3,
                size=5,
                total=repository.find_count(models.Book)
            )
        )
        assert len(books) == 1

    def test_find_by_id_returns_requested_model(
        self, resources, fantasy_database, repository, models
    ):
        book = repository.find_by_id(models.Book, id='11')
        assert isinstance(book, models.Book)
        assert book.id == 11

    def test_find_by_id_raises_error_if_model_not_found(
        self, resources, repository, models
    ):
        with pytest.raises(exc.ResourceNotFound) as exc_info:
            repository.find_by_id(
                model_class=models.Book,
                id='123123',
            )
        assert exc_info.value.id == '123123'

    def test_find_by_id_loads_included_relations(
        self, resources, repository, fantasy_database, models
    ):
        include = IncludeParameter(
            resources,
            type='books',
            include='author.books,chapters'
        )
        book = repository.find_by_id(models.Book, id='11', include=include)
        queries_before = len(get_debug_queries())
        book.author.books
        book.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0

    def test_find_count(self, fantasy_database, repository, models):
        count = repository.find_count(model_class=models.Book)
        assert count == 11
