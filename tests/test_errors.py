import pytest

from flask_jsonapi import errors


class TestError(object):
    @pytest.fixture
    def error(self):
        return errors.Error()

    def test_code(self, error):
        assert error.code == 'Error'

    def test_error_properties_are_null_by_default(self, error):
        assert error.id is None
        assert error.status is None
        assert error.title is None
        assert error.detail is None
        assert error.source_pointer is None
        assert error.source_parameter is None
        assert error.meta is None

    def test_source_when_no_pointer_or_parameter(self, error):
        assert error.source is None

    def test_source_when_error_has_pointer(self, error):
        error.source_pointer = '/data'
        assert error.source == {'pointer': '/data'}

    def test_source_when_error_has_parameter(self, error):
        error.source_parameter = '/data'
        assert error.source == {'parameter': '/data'}

    def test_as_dict(self, error):
        error.title = 'Error title'
        error.detail = 'Error detail'
        assert error.as_dict == {
            'code': 'Error',
            'title': 'Error title',
            'detail': 'Error detail'
        }


class TestResourceTypeNotFound(object):
    @pytest.fixture
    def error(self):
        return errors.ResourceTypeNotFound(type='foobars')

    def test_status(self, error):
        assert error.status == '404'

    def test_title(self, error):
        assert error.title == 'Resource type not found'

    def test_detail(self, error):
        assert error.detail == 'foobars is not a valid resource type.'


class TestResourceNotFound(object):
    @pytest.fixture
    def error(self):
        return errors.ResourceNotFound(type='books', id='123')

    def test_status(self, error):
        assert error.status == '404'

    def test_title(self, error):
        assert error.title == 'Resource not found'

    def test_detail(self, error):
        assert error.detail == (
            'The resource identified by (books, 123) type-id pair '
            'could not be found.'
        )


class TestRelationshipNotFound(object):
    @pytest.fixture
    def error(self):
        return errors.RelationshipNotFound(type='books', relationship='foobar')

    def test_status(self, error):
        assert error.status == '404'

    def test_title(self, error):
        assert error.title == 'Relationship not found'

    def test_detail(self, error):
        assert error.detail == 'foobar is not a valid relationship for books.'


class TestFieldTypeMissing(object):
    @pytest.fixture
    def error(self):
        return errors.FieldTypeMissing()

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Field type missing'

    def test_detail(self, error):
        assert error.detail == 'fields must specify a type.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'fields'


class TestInvalidFieldFormat(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidFieldFormat(type='books')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid field format'

    def test_detail(self, error):
        assert error.detail == (
            'The value of fields[books] parameter must be a '
            'comma-separated list that refers to the name(s) '
            'of the fields to be returned.'
        )

    def test_source_parameter(self, error):
        assert error.source_parameter == 'fields[books]'


class TestInvalidFieldType(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidFieldType(type='foobars')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid field'

    def test_detail(self, error):
        assert error.detail == 'foobars is not a valid resource type.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'fields[foobars]'


class TestInvalidField(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidField(type='books', field='foobar')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid field'

    def test_detail(self, error):
        assert error.detail == 'foobar is not a valid field for books.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'fields[books]'


class TestInvalidIncludeFormat(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidIncludeFormat()

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid include format'

    def test_detail(self, error):
        assert error.detail == (
            'The value of include parameter must be a comma-separated '
            'list of relationship paths.'
        )

    def test_source_parameter(self, error):
        assert error.source_parameter == 'include'


class TestInvalidInclude(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidInclude(type='books', relationship='foobar')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid include'

    def test_detail(self, error):
        assert error.detail == 'foobar is not a valid relationship of books.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'include'


class TestInvalidSortFormat(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidSortFormat()

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid sort format'

    def test_detail(self, error):
        assert error.detail == (
            'The sort parameter must be a comma-separated list of '
            'sort fields.'
        )

    def test_source_parameter(self, error):
        assert error.source_parameter == 'sort'


class TestInvalidSortField(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidSortField(type='books', field='foobar')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid sort field'

    def test_detail(self, error):
        assert error.detail == 'foobar is not a sortable field for books.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'sort'


class TestInvalidPageFormat(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidPageFormat()

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid page format'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'page'


class TestInvalidPageParameter(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidPageParameter(param='foo')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid page parameter'

    def test_detail(self, error):
        assert error.detail == 'foo is not a valid page parameter.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'page[foo]'


class TestInvalidPageValue(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidPageValue(
            param='offset',
            detail='offset must be at least 0'
        )

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Invalid page value'

    def test_detail(self, error):
        assert error.detail == 'offset must be at least 0'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'page[offset]'


class TestParameterNotAllowed(object):
    @pytest.fixture
    def error(self):
        return errors.ParameterNotAllowed(source_parameter='foo')

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Parameter not allowed'

    def test_detail(self, error):
        assert error.detail == 'foo is not a valid parameter.'

    def test_source_parameter(self, error):
        assert error.source_parameter == 'foo'


class TestInvalidJSON(object):
    @pytest.fixture
    def error(self):
        return errors.InvalidJSON(
            detail='Expecting object: line 1 column 1 (char 0)'
        )

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Request body is not valid JSON'

    def test_detail(self, error):
        assert error.detail == 'Expecting object: line 1 column 1 (char 0)'


class TestValidationError(object):
    @pytest.fixture
    def error(self):
        return errors.ValidationError(
            detail='data must be an object',
            source_pointer='/data'
        )

    def test_status(self, error):
        assert error.status == '400'

    def test_title(self, error):
        assert error.title == 'Validation error'

    def test_detail(self, error):
        assert error.detail == 'data must be an object'

    def test_source_pointer(self, error):
        assert error.source_pointer == '/data'


class TestTypeMismatch(object):
    @pytest.fixture
    def error(self):
        return errors.TypeMismatch(type='foobar', source_pointer='/data/type')

    def test_status(self, error):
        assert error.status == '409'

    def test_title(self, error):
        assert error.title == 'Type mismatch'

    def test_detail(self, error):
        assert error.detail == 'foobar is not a valid type for this operation.'

    def test_source_pointer(self, error):
        assert error.source_pointer == '/data/type'


class TestIDMismatch(object):
    @pytest.fixture
    def error(self):
        return errors.IDMismatch(id='123')

    def test_status(self, error):
        assert error.status == '409'

    def test_title(self, error):
        assert error.title == 'ID mismatch'

    def test_detail(self, error):
        assert error.detail == '123 does not match the endpoint id.'

    def test_source_pointer(self, error):
        assert error.source_pointer == '/data/id'


class TestFullReplacementDisallowed(object):
    @pytest.fixture
    def error(self):
        return errors.FullReplacementDisallowed(
            relationship='books',
            source_pointer='/data/relationships/books'
        )

    def test_status(self, error):
        assert error.status == '403'

    def test_title(self, error):
        assert error.title == 'Full replacement disallowed'

    def test_detail(self, error):
        assert error.detail == 'Full replacement of books is not allowed.'

    def test_source_pointer(self, error):
        assert error.source_pointer == '/data/relationships/books'


class TestClientGeneratedIDsUnsupported(object):
    @pytest.fixture
    def error(self):
        return errors.ClientGeneratedIDsUnsupported(type='books')

    def test_status(self, error):
        assert error.status == '403'

    def test_title(self, error):
        assert error.title == 'Client-generated IDs unsupported'

    def test_detail(self, error):
        assert error.detail == (
            'The server does not support creation of books resource '
            'with a client-generated ID.'
        )

    def test_source_pointer(self, error):
        return error.source_pointer == '/data/id'


class TestResourceAlreadyExists(object):
    @pytest.fixture
    def error(self):
        return errors.ResourceAlreadyExists(type='books', id='1')

    def test_status(self, error):
        assert error.status == '409'

    def test_title(self, error):
        assert error.title == 'Resource already exists'

    def test_detail(self, error):
        assert error.detail == (
            'A resource with (books, 1) type-id pair already exists.'
        )
