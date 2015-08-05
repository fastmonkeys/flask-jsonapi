import pytest
from flask_sqlalchemy import get_debug_queries

from flask_jsonapi import exc
from flask_jsonapi.params import IncludeParameter
from flask_jsonapi.repository import SQLAlchemyRepository


class TestSQLAlchemyRepository(object):
    @pytest.fixture
    def repository(self, db):
        return SQLAlchemyRepository(db.session)

    @pytest.fixture
    def book(self, db, models, fantasy_database):
        return db.session.query(models.Book).filter_by(id=1).one()

    def test_find_by_id_returns_requested_model(
        self, resources, book, repository, models
    ):
        include = IncludeParameter(resources, type='books', include=None)
        model = repository.find_by_id(
            model_class=models.Book,
            id=repository.get_id(book),
            include=include
        )
        assert model is book

    def test_find_by_id_raises_error_if_model_not_found(
        self, resources, repository, models
    ):
        include = IncludeParameter(resources, type='books', include=None)
        with pytest.raises(exc.ResourceNotFound) as exc_info:
            repository.find_by_id(
                model_class=models.Book,
                id='123123',
                include=include
            )
        assert exc_info.value.id == '123123'

    def test_find_by_id_loads_included_relations(
        self, resources, repository, book, models
    ):
        include = IncludeParameter(
            resources,
            type='books',
            include='author.books,chapters'
        )
        model = repository.find_by_id(
            model_class=models.Book,
            id=repository.get_id(book),
            include=include
        )
        queries_before = len(get_debug_queries())
        model.author.books
        model.chapters
        queries_after = len(get_debug_queries())
        assert queries_after - queries_before == 0
