from flask_jsonapi import errors


class TestInvalidResource(object):
    def test_errors(self):
        e = errors.InvalidResource('foobars')
        assert e.errors == [
            {
                "code": 'INVALID_RESOURCE',
                "status": 404,
                "title": "Invalid resource",
                "detail": "foobars is not a valid resource"
            }
        ]


class TestResourceNotFound(object):
    def test_errors(self):
        e = errors.ResourceNotFound(type='books', id='123')
        assert e.errors == [
            {
                "code": 'RESOURCE_NOT_FOUND',
                "status": 404,
                "title": "Resource not found",
                "detail": (
                    "The resource identified by (books, 123) type-id pair "
                    "could not be found."
                )
            }
        ]


class TestFieldTypeMissing(object):
    def test_errors(self):
        e = errors.FieldTypeMissing()
        assert e.errors == [
            {
                "code": "FIELD_TYPE_MISSING",
                "status": 400,
                "title": "Field type missing",
                "detail": "fields must specify a type.",
                "source": {
                    "parameter": "fields"
                }
            }
        ]


class TestInvalidFieldFormat(object):
    def test_errors(self):
        e = errors.InvalidFieldFormat('books')
        assert e.errors == [
            {
                "code": "INVALID_FIELD_FORMAT",
                "status": 400,
                "title": "Invalid field format",
                "detail": (
                    "The value of fields[books] parameter must be a "
                    "comma-separated list that refers to the name(s) "
                    "of the fields to be returned."
                ),
                "source": {
                    "parameter": "fields[books]"
                }
            }
        ]


class TestInvalidFieldType(object):
    def test_errors(self):
        e = errors.InvalidFieldType('foobars')
        assert e.errors == [
            {
                "code": "INVALID_FIELD_TYPE",
                "status": 400,
                "title": "Invalid field",
                "detail": "foobars is not a valid resource.",
                "source": {
                    "parameter": "fields[foobars]"
                }
            }
        ]


class TestInvalidField(object):
    def test_errors(self):
        e = errors.InvalidField('books', 'foobar')
        assert e.errors == [
            {
                "code": "INVALID_FIELD",
                "status": 400,
                "title": "Invalid field",
                "detail": "foobar is not a valid field for books.",
                "source": {
                    "parameter": "fields[books]"
                }
            }
        ]


class TestInvalidIncludeFormat(object):
    def test_errors(self):
        e = errors.InvalidIncludeFormat()
        assert e.errors == [
            {
                "code": "INVALID_INCLUDE_FORMAT",
                "status": 400,
                "title": "Invalid include format",
                "detail": (
                    "The value of include parameter must be a comma-separated "
                    "list of relationship paths."
                ),
                "source": {
                    "parameter": "include"
                }
            }
        ]


class TestInvalidInclude(object):
    def test_errors(self):
        e = errors.InvalidInclude('books', 'foobar')
        assert e.errors == [
            {
                "code": "INVALID_INCLUDE",
                "status": 400,
                "title": "Invalid include",
                "detail": "foobar is not a valid relationship of books.",
                "source": {
                    "parameter": "include"
                }
            }
        ]


class TestInvalidSortFormat(object):
    def test_errors(self):
        e = errors.InvalidSortFormat()
        assert e.errors == [
            {
                "code": "INVALID_SORT_FORMAT",
                "status": 400,
                "title": "Invalid sort format",
                "detail": (
                    "The sort parameter must be a comma-separated list of "
                    "sort fields."
                ),
                "source": {
                    "parameter": "sort"
                }
            }
        ]


class TestInvalidSortField(object):
    def test_errors(self):
        e = errors.InvalidSortField('books', 'foobar')
        assert e.errors == [
            {
                "code": "INVALID_SORT_FIELD",
                "status": 400,
                "title": "Invalid sort field",
                "detail": "foobar is not a sortable field for books",
                "source": {
                    "parameter": "sort"
                }
            }
        ]


class TestInvalidPageFormat(object):
    def test_errors(self):
        e = errors.InvalidPageFormat()
        assert e.errors == [
            {
                "status": 400,
                "code": "INVALID_PAGE_FORMAT",
                "title": "Invalid page format",
                "source": {
                    "parameter": "page"
                }
            }
        ]


class TestInvalidPageParameters(object):
    def test_errors(self):
        e = errors.InvalidPageParameters({'foo', 'bar'})
        assert e.errors == [
            {
                "status": 400,
                "code": "INVALID_PAGE_PARAMETER",
                "title": "Invalid page parameter",
                "detail": "bar is not a valid page parameter",
                "source": {
                    "parameter": "page[bar]"
                }
            },
            {
                "status": 400,
                "code": "INVALID_PAGE_PARAMETER",
                "title": "Invalid page parameter",
                "detail": "foo is not a valid page parameter",
                "source": {
                    "parameter": "page[foo]"
                }
            },
        ]


class TestInvalidPageValue(object):
    def test_errors(self):
        e = errors.InvalidPageValue('offset', 'offset must be at least 0')
        assert e.errors == [
            {
                "status": 400,
                "code": 'INVALID_PAGE_VALUE',
                "title": "Invalid page value",
                "detail": "offset must be at least 0",
                "source": {
                    "parameter": "page[offset]"
                }
            }
        ]
