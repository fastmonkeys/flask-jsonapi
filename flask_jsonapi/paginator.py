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


class PagedPagination(Pagination):
    def __init__(self, number, size):
        self.number = number
        self.size = size

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
    allowed_params = {'number', 'size'}
    pagination_class = PagedPagination

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
        for key in keys:
            if key not in self.allowed_params:
                raise errors.InvalidPageParameter(param=key)

    def _validate(self, params):
        try:
            params['number'] = int(params.get('number', 1))
        except ValueError:
            raise errors.InvalidPageValue(
                param='number',
                detail='number must be an integer'
            )

        try:
            params['size'] = int(params.get('size', self.default_page_size))
        except ValueError:
            raise errors.InvalidPageValue(
                param='size',
                detail='size must be an integer'
            )

        if params['size'] < 1:
            raise errors.InvalidPageValue(
                param='size',
                detail='size must be at least 1'
            )

        if params['size'] > self.max_page_size:
            raise errors.InvalidPageValue(
                param='size',
                detail='size cannot exceed maximum page size of {}'.format(
                    self.max_page_size
                )
            )

        if params['number'] < 1:
            raise errors.InvalidPageValue(
                param='number',
                detail='number must be at least 1'
            )

        return params
