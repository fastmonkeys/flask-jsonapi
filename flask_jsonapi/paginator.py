import math

from . import errors


class Pagination(object):
    def get_link_params(self, count):
        return {
            'first': self.get_first(),
            'last': self.get_last(count),
            'prev': self.get_prev() if self.has_prev() else None,
            'next': self.get_next() if self.has_next(count) else None,
        }


class OffsetPagination(Pagination):
    def __init__(self, offset, limit):
        self.offset = offset
        self.limit = limit

    def get_first(self):
        return {
            'offset': 0,
            'limit': self.limit
        }

    def has_prev(self):
        return self.offset > 0

    def get_prev(self):
        return {
            'offset': max(self.offset - self.limit, 0),
            'limit': self.limit
        }

    def has_next(self, count):
        return self.offset + self.limit < count

    def get_next(self):
        return {
            'offset': self.offset + self.limit,
            'limit': self.limit
        }

    def get_last(self, count):
        return {
            'offset': count - self.limit,
            'limit': self.limit
        }

    def __repr__(self):
        return '<OffsetPagination offset={offset} limit={limit}>'.format(
            offset=self.offset,
            limit=self.limit
        )


class PagedPagination(Pagination):
    def __init__(self, number, size):
        self.number = number
        self.size = size

    @property
    def offset(self):
        return (self.number - 1) * self.size

    @property
    def limit(self):
        return self.size

    def get_first(self):
        return {
            'number': 1,
            'size': self.size
        }

    def has_prev(self):
        return self.number > 1

    def get_prev(self):
        return {
            'number': self.number - 1,
            'size': self.size
        }

    def has_next(self, count):
        return self.number < self.get_pages(count)

    def get_next(self):
        return {
            'number': self.number + 1,
            'size': self.size
        }

    def get_last(self, count):
        return {
            'number': self.get_pages(count),
            'size': self.size
        }

    def get_pages(self, count):
        return int(math.ceil(count / float(self.size)))

    def __repr__(self):
        return '<PagedPagination number={number} size={size}>'.format(
            number=self.number,
            size=self.size
        )


class Paginator(object):
    def __init__(self, default_page_size=20, max_page_size=100):
        self.max_page_size = max_page_size
        self.default_page_size = default_page_size

    def paginate(self, params):
        self._check_extra_params(params)
        params = self._validate(params)
        return self.pagination_class(**params)

    def _check_extra_params(self, params):
        try:
            keys = params.keys()
        except AttributeError:
            raise errors.InvalidPageFormat()
        extra_params = set(keys) - self.allowed_params
        if extra_params:
            raise errors.InvalidPageParameters(extra_params)

    def _validate(self, params):
        return params


class OffsetPaginator(Paginator):
    allowed_params = {'offset', 'limit'}
    pagination_class = OffsetPagination

    def _validate(self, params):
        try:
            params['offset'] = int(params.get('offset', 0))
        except ValueError:
            raise errors.InvalidPageValue('offset', 'offset must be an integer')

        try:
            params['limit'] = int(params.get('limit', self.default_page_size))
        except ValueError:
            raise errors.InvalidPageValue('limit', 'limit must be an integer')

        if params['limit'] < 1:
            raise errors.InvalidPageValue('limit', 'limit must be at least 1')

        if params['limit'] > self.max_page_size:
            raise errors.InvalidPageValue(
                'limit',
                'limit cannot exceed maximum page size of {}'.format(
                    self.max_page_size
                )
            )

        if params['offset'] < 0:
            raise errors.InvalidPageValue('offset', 'offset must be at least 0')

        return params


class PagedPaginator(Paginator):
    allowed_params = {'number', 'size'}
    pagination_class = PagedPagination

    def _validate(self, params):
        try:
            params['number'] = int(params.get('number', 1))
        except ValueError:
            raise errors.InvalidPageValue('number', 'number must be an integer')

        try:
            params['size'] = int(params.get('size', self.default_page_size))
        except ValueError:
            raise errors.InvalidPageValue('size', 'size must be an integer')

        if params['size'] < 1:
            raise errors.InvalidPageValue('size', 'size must be at least 1')

        if params['size'] > self.max_page_size:
            raise errors.InvalidPageValue(
                'size',
                'size cannot exceed maximum page size of {}'.format(
                    self.max_page_size
                )
            )

        if params['number'] < 1:
            raise errors.InvalidPageValue('number', 'number must be at least 1')

        return params
