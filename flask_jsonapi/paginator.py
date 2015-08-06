import math

from . import exc


class Pagination(object):
    @property
    def link_params(self):
        return {
            'first': self.first,
            'last': self.last,
            'prev': self.prev if self.has_prev else None,
            'next': self.next if self.has_next else None,
        }


class OffsetPagination(Pagination):
    def __init__(self, offset, limit, count):
        self.offset = offset
        self.limit = limit
        self.count = count

    @property
    def first(self):
        return {
            'offset': 0,
            'limit': self.limit
        }

    @property
    def has_prev(self):
        return self.offset > 0

    @property
    def prev(self):
        return {
            'offset': max(self.offset - self.limit, 0),
            'limit': self.limit
        }

    @property
    def has_next(self):
        return self.offset + self.limit < self.count

    @property
    def next(self):
        return {
            'offset': self.offset + self.limit,
            'limit': self.limit
        }

    @property
    def last(self):
        return {
            'offset': self.count - self.offset,
            'limit': self.limit
        }

    def __repr__(self):
        return '<OffsetPagination offset={offset} limit={limit}>'.format(
            offset=self.offset,
            limit=self.limit
        )


class PagedPagination(Pagination):
    def __init__(self, number, size, count):
        self.number = number
        self.size = size
        self.count = count

    @property
    def first(self):
        return {
            'number': 1,
            'size': self.size
        }

    @property
    def has_prev(self):
        return self.number > 1

    @property
    def prev(self):
        return {
            'number': self.number - 1,
            'size': self.size
        }

    @property
    def has_next(self):
        return self.number < self.pages

    @property
    def next(self):
        return {
            'number': self.number + 1,
            'size': self.size
        }

    @property
    def last(self):
        return {
            'number': self.pages,
            'size': self.size
        }

    @property
    def offset(self):
        return (self.number - 1) * self.size

    @property
    def limit(self):
        return self.size

    @property
    def pages(self):
        return int(math.ceil(self.count / float(self.size)))

    def __repr__(self):
        return '<PagedPagination number={number} size={size}>'.format(
            number=self.number,
            size=self.size
        )


class Paginator(object):
    def __init__(self, default_page_size=20, max_page_size=100):
        self.max_page_size = max_page_size
        self.default_page_size = default_page_size

    def paginate(self, params, count):
        self._check_extra_params(params)
        params = self._validate(params)
        return self.pagination_class(count=count, **params)

    def _check_extra_params(self, params):
        try:
            keys = params.keys()
        except AttributeError:
            raise exc.InvalidPageValue(None, 'invalid value for page parameter')
        extra_params = set(keys) - self.allowed_params
        if extra_params:
            raise exc.InvalidPageParameters(extra_params)

    def _validate(self, params):
        return params


class OffsetPaginator(Paginator):
    allowed_params = {'offset', 'limit'}
    pagination_class = OffsetPagination

    def _validate(self, params):
        try:
            params['offset'] = int(params.get('offset', 0))
        except ValueError:
            raise exc.InvalidPageValue('offset', 'offset must be an integer')

        try:
            params['limit'] = int(params.get('limit', self.default_page_size))
        except ValueError:
            raise exc.InvalidPageValue('limit', 'limit must be an integer')

        if params['limit'] < 1:
            raise exc.InvalidPageValue('limit', 'limit must be at least 1')

        if params['limit'] > self.max_page_size:
            raise exc.InvalidPageValue(
                'limit',
                'limit cannot exceed maximum page size of {}'.format(
                    self.max_page_size
                )
            )

        if params['offset'] < 0:
            raise exc.InvalidPageValue('offset', 'offset must be at least 0')

        return params


class PagedPaginator(Paginator):
    allowed_params = {'number', 'size'}
    pagination_class = PagedPagination

    def _validate(self, params):
        try:
            params['number'] = int(params.get('number', 1))
        except ValueError:
            raise exc.InvalidPageValue('number', 'number must be an integer')

        try:
            params['size'] = int(params.get('size', self.default_page_size))
        except ValueError:
            raise exc.InvalidPageValue('size', 'size must be an integer')

        if params['size'] < 1:
            raise exc.InvalidPageValue('size', 'size must be at least 1')

        if params['size'] > self.max_page_size:
            raise exc.InvalidPageValue(
                'size',
                'size cannot exceed maximum page size of {}'.format(
                    self.max_page_size
                )
            )

        if params['number'] < 1:
            raise exc.InvalidPageValue('number', 'number must be at least 1')

        return params
