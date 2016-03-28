import pytest

from flask_jsonapi import errors
from flask_jsonapi.paginator import Pagination, Paginator


class TestPagination(object):
    def test_first(self):
        pagination = Pagination(number=2, size=25)
        assert pagination.get_first() == {
            'number': 1,
            'size': 25
        }

    def test_last(self):
        pagination = Pagination(number=2, size=25)
        assert pagination.get_last(count=157) == {
            'number': 7,
            'size': 25
        }

    def test_has_prev(self):
        pagination = Pagination(number=1, size=25)
        assert pagination.has_prev() is False

        pagination = Pagination(number=2, size=25)
        assert pagination.has_prev() is True

    def test_prev(self):
        pagination = Pagination(number=2, size=25)
        assert pagination.get_prev() == {
            'number': 1,
            'size': 25
        }

    def test_has_next(self):
        pagination = Pagination(number=6, size=25)
        assert pagination.has_next(count=157) is True

        pagination = Pagination(number=7, size=25)
        assert pagination.has_next(count=157) is False

    def test_next(self):
        pagination = Pagination(number=2, size=25)
        assert pagination.get_next() == {
            'number': 3,
            'size': 25
        }

    def test_link_params(self):
        pagination = Pagination(number=7, size=25)
        assert pagination.get_link_params(count=157) == {
            'first': {
                'number': 1,
                'size': 25,
            },
            'last': {
                'number': 7,
                'size': 25,
            },
            'prev': {
                'number': 6,
                'size': 25,
            },
            'next': None,
        }
