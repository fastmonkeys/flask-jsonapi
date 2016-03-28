import pytest

from flask_jsonapi.errors import (
    InvalidField,
    InvalidFieldsFormat,
    InvalidFieldsValueFormat,
    InvalidInclude,
    InvalidIncludeFormat,
    InvalidPageFormat,
    InvalidPageParameter,
    InvalidPageValue,
    InvalidResourceType,
    JSONAPIException
)
from flask_jsonapi.params import (
    Page,
    parse_fields_parameter,
    parse_include_parameter,
    parse_page_parameter
)


class TestParseFieldsParameter(object):
    def test_missing_fields_parameter(self, resource_registry):
        fields = parse_fields_parameter(resource_registry, value=None)
        assert fields == {}

    def test_invalid_fields_format(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_fields_parameter(
                resource_registry,
                value='invalid'
            )
        assert isinstance(excinfo.value.errors[0], InvalidFieldsFormat)

    def test_invalid_resource_type(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_fields_parameter(
                resource_registry,
                value={'invalid': ''}
            )
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidResourceType)
        assert error.type == 'invalid'

    def test_invalid_field(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_fields_parameter(
                resource_registry,
                value={'series': 'invalid'}
            )
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidField)
        assert error.type == 'series'
        assert error.field == 'invalid'

    def test_invalid_fields_value_format(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_fields_parameter(
                resource_registry,
                value={'series': ['foo', 'bar']}
            )
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidFieldsValueFormat)
        assert error.type == 'series'

    def test_valid_fields_parameter(self, resource_registry):
        fields = parse_fields_parameter(
            resource_registry,
            value={
                'books': 'title,date_published,author',
                'authors': 'name',
            }
        )

        assert len(fields) == 2
        assert fields['books'] == {'title', 'date_published', 'author'}
        assert fields['authors'] == {'name'}


class TestParseIncludeParameter(object):
    @pytest.mark.parametrize(
        ('input', 'output'),
        [
            (None, {}),
            ('', {}),
            ('books', {'books': {}}),
            ('books.author', {'books': {'author': {}}}),
            ('books.author,books', {'books': {'author': {}}}),
        ]
    )
    def test_valid_include(self, resource_registry, input, output):
        assert parse_include_parameter(
            resource=resource_registry.by_type['stores'],
            value=input
        ) == output

    def test_invalid_relationship(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_include_parameter(
                resource=resource_registry.by_type['stores'],
                value='books.invalid'
            )
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidInclude)
        assert error.type == 'books'
        assert error.relationship == 'invalid'

    def test_invalid_format(self, resource_registry):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_include_parameter(
                resource=resource_registry.by_type['stores'],
                value={'foo': 'bar'}
            )
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidIncludeFormat)


class TestParsePageParameter(object):
    @pytest.fixture
    def resource(self, resource_registry):
        return resource_registry.by_type['books']

    def test_extra_parameters_raises_error(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'foo': 'bar'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageParameter)
        assert error.source_parameter == 'page[foo]'

    def test_defaults(self, resource):
        page = parse_page_parameter(resource=resource, value=None)
        assert page == Page(number=1, size=20)

    def test_custom_page(self, resource):
        page = parse_page_parameter(
            resource=resource,
            value={'number': '2', 'size': '50'}
        )
        assert page == Page(number=2, size=50)

    def test_too_low_size_raises_error(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'size': '0'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageValue)
        assert error.source_parameter == 'page[size]'

    def test_too_high_size_raises_error(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'size': '101'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageValue)
        assert error.detail == 'Page size exceeds the maximum page size of 100'
        assert error.source_parameter == 'page[size]'

    def test_too_low_number_raises_error(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'number': '0'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageValue)
        assert error.source_parameter == 'page[number]'

    def test_invalid_number_type(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'number': 'foobar'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageValue)
        assert error.source_parameter == 'page[number]'

    def test_invalid_size_type(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value={'size': 'foobar'})
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageValue)
        assert error.source_parameter == 'page[size]'

    def test_invalid_format(self, resource):
        with pytest.raises(JSONAPIException) as excinfo:
            parse_page_parameter(resource=resource, value='foobar')
        error = excinfo.value.errors[0]
        assert isinstance(error, InvalidPageFormat)
