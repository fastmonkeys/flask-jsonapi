class PaginationLinkParameters(object):
    def __init__(self, pagination, count):
        self.pagination = pagination
        self.count = count

    def get_link_params(self):
        return {
            'first': self.first,
            'last': self.last,
            'prev': self.prev if self.has_prev else None,
            'next': self.next if self.has_next else None,
        }

    @property
    def first(self):
        return {
            'number': 1,
            'size': self.pagination.size
        }

    @property
    def has_prev(self):
        return self.pagination.number > 1

    @property
    def prev(self):
        return {
            'number': self.pagination.number - 1,
            'size': self.pagination.size
        }

    @property
    def has_next(self):
        return self.pagination.number < self.get_pages(self.count)

    @property
    def next(self):
        return {
            'number': self.pagination.number + 1,
            'size': self.pagination.size
        }

    @property
    def last(self):
        return {
            'number': self.pages,
            'size': self.pagination.size
        }

    @property
    def pages(self):
        full_pages, remainder = divmod(self.count, self.pagination.size)
        return full_pages + 1 if remainder else full_pages


class Pagination(object):
    def __init__(self, number, size):
        self.number = number
        self.size = size
