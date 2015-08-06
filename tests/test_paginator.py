import pytest

from flask_jsonapi import exc
from flask_jsonapi.paginator import (
    OffsetPagination,
    OffsetPaginator,
    PagedPagination,
    PagedPaginator
)


class TestOffsetPagination(object):
    def test_first(self):
        pagination = OffsetPagination(offset=25, limit=25, count=157)
        assert pagination.first == {
            'offset': 0,
            'limit': 25
        }

    def test_last(self):
        pagination = OffsetPagination(offset=25, limit=25, count=157)
        assert pagination.last == {
            'offset': 132,
            'limit': 25
        }

    def test_has_prev(self):
        pagination = OffsetPagination(offset=0, limit=25, count=157)
        assert pagination.has_prev is False

        pagination = OffsetPagination(offset=1, limit=25, count=157)
        assert pagination.has_prev is True

    def test_prev(self):
        pagination = OffsetPagination(offset=10, limit=25, count=157)
        assert pagination.prev == {
            'offset': 0,
            'limit': 25
        }

        pagination = OffsetPagination(offset=50, limit=25, count=157)
        assert pagination.prev == {
            'offset': 25,
            'limit': 25
        }

    def test_has_next(self):
        pagination = OffsetPagination(offset=131, limit=25, count=157)
        assert pagination.has_next is True

        pagination = OffsetPagination(offset=132, limit=25, count=157)
        assert pagination.has_next is False

    def test_next(self):
        pagination = OffsetPagination(offset=25, limit=25, count=157)
        assert pagination.next == {
            'offset': 50,
            'limit': 25
        }

    def test_link_params(self):
        pagination = OffsetPagination(offset=0, limit=25, count=157)
        assert pagination.link_params == {
            'first': {
                'offset': 0,
                'limit': 25,
            },
            'last': {
                'offset': 157,
                'limit': 25,
            },
            'prev': None,
            'next': {
                'offset': 25,
                'limit': 25,
            },
        }


class TestPagedPagination(object):
    def test_first(self):
        pagination = PagedPagination(number=2, size=25, count=157)
        assert pagination.first == {
            'number': 1,
            'size': 25
        }

    def test_last(self):
        pagination = PagedPagination(number=2, size=25, count=157)
        assert pagination.last == {
            'number': 7,
            'size': 25
        }

    def test_has_prev(self):
        pagination = PagedPagination(number=1, size=25, count=157)
        assert pagination.has_prev is False

        pagination = PagedPagination(number=2, size=25, count=157)
        assert pagination.has_prev is True

    def test_prev(self):
        pagination = PagedPagination(number=2, size=25, count=157)
        assert pagination.prev == {
            'number': 1,
            'size': 25
        }

    def test_has_next(self):
        pagination = PagedPagination(number=6, size=25, count=157)
        assert pagination.has_next is True

        pagination = PagedPagination(number=7, size=25, count=157)
        assert pagination.has_next is False

    def test_next(self):
        pagination = PagedPagination(number=2, size=25, count=157)
        assert pagination.next == {
            'number': 3,
            'size': 25
        }

    def test_link_params(self):
        pagination = PagedPagination(number=7, size=25, count=157)
        assert pagination.link_params == {
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


class TestOffsetPaginator(object):
    def test_extra_parameters_raises_error(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageParameters) as exc_info:
            paginator.paginate({'foo': 'bar'}, count=10)
        assert exc_info.value.params == {'foo'}

    def test_defaults(self):
        paginator = OffsetPaginator()
        pagination = paginator.paginate({}, count=10)
        assert pagination.offset == 0
        assert pagination.limit == 20

    def test_too_low_limit_raises_error(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'limit': '0'}, count=10)
        assert exc_info.value.param == 'limit'
        assert exc_info.value.message == 'limit must be at least 1'

    def test_too_high_limit_raises_error(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'limit': '101'}, count=10)
        assert exc_info.value.param == 'limit'
        assert exc_info.value.message == (
            'limit cannot exceed maximum page size of 100'
        )

    def test_too_low_offset_raises_error(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'offset': '-1'}, count=10)
        assert exc_info.value.param == 'offset'
        assert exc_info.value.message == 'offset must be at least 0'

    def test_invalid_offset_type(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'offset': 'foobar'}, count=10)
        assert exc_info.value.param == 'offset'
        assert exc_info.value.message == 'offset must be an integer'

    def test_invalid_limit_type(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'limit': 'foobar'}, count=10)
        assert exc_info.value.param == 'limit'
        assert exc_info.value.message == 'limit must be an integer'

    def test_invalid_params(self):
        paginator = OffsetPaginator()
        with pytest.raises(exc.InvalidPageFormat):
            paginator.paginate('foobar', count=10)


class TestPagedPaginator(object):
    def test_extra_parameters_raises_error(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageParameters) as exc_info:
            paginator.paginate({'foo': 'bar'}, count=10)
        assert exc_info.value.params == {'foo'}

    def test_defaults(self):
        paginator = PagedPaginator()
        pagination = paginator.paginate({}, count=10)
        assert pagination.number == 1
        assert pagination.size == 20

    def test_too_low_size_raises_error(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'size': '0'}, count=10)
        assert exc_info.value.message == 'size must be at least 1'

    def test_too_high_size_raises_error(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'size': '101'}, count=10)
        assert exc_info.value.message == (
            'size cannot exceed maximum page size of 100'
        )

    def test_too_low_number_raises_error(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'number': '0'}, count=10)
        assert exc_info.value.message == 'number must be at least 1'

    def test_invalid_number_type(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'number': 'foobar'}, count=10)
        assert exc_info.value.message == 'number must be an integer'

    def test_invalid_size_type(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageValue) as exc_info:
            paginator.paginate({'size': 'foobar'}, count=10)
        assert exc_info.value.message == 'size must be an integer'

    def test_invalid_params(self):
        paginator = PagedPaginator()
        with pytest.raises(exc.InvalidPageFormat):
            paginator.paginate('foobar', count=10)
