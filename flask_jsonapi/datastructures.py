from collections import namedtuple

Page = namedtuple('Page', ['number', 'size'])


class Pagination(object):
    def __init__(self, page, total, models):
        self.page = page
        self.total = total
        self.models = models

    @property
    def first(self):
        return Page(number=1, size=self.page.size)

    @property
    def has_prev(self):
        return self.page.number > 1

    @property
    def prev(self):
        return Page(number=self.page.number - 1, size=self.page.size)

    @property
    def has_next(self):
        return self.page.number < self.pages

    @property
    def next(self):
        return Page(number=self.page.number + 1, size=self.page.size)

    @property
    def last(self):
        return Page(number=self.pages, size=self.page.size)

    @property
    def pages(self):
        full_pages, remainder = divmod(self.total, self.page.size)
        return full_pages + 1 if remainder else full_pages
