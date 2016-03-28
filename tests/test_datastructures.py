import pytest

from flask_jsonapi.datastructures import Page, Pagination


class TestPagination(object):
    @pytest.fixture
    def pagination(self):
        return Pagination(
            page=Page(number=2, size=25),
            total=157,
            models=[]
        )

    def test_first(self, pagination):
        assert pagination.first == Page(number=1, size=25)

    def test_last(self, pagination):
        assert pagination.last == Page(number=7, size=25)

    def test_has_prev(self, pagination):
        assert pagination.has_prev is True

        pagination.page = Page(number=1, size=25)
        assert pagination.has_prev is False

    def test_prev(self, pagination):
        assert pagination.prev == Page(number=1, size=25)

    def test_has_next(self, pagination):
        assert pagination.has_next is True

        pagination.page = Page(number=7, size=25)
        assert pagination.has_next is False

    def test_next(self, pagination):
        assert pagination.next == Page(number=3, size=25)

    def test_pages(self, pagination):
        assert pagination.pages == 7
