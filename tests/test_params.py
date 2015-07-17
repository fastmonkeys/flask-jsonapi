import pytest
from flask import Request
from werkzeug.test import EnvironBuilder

from flask_jsonapi import exc
from flask_jsonapi.params import FieldsParameter, IncludeParameter, Parameters


class TestParameters(object):
    @pytest.fixture
    def http_request(self):
        builder = EnvironBuilder(
            query_string='fields[books]=title&include=books'
        )
        env = builder.get_environ()
        return Request(env)

    @pytest.fixture
    def params(self, resources, http_request):
        return Parameters(resources, 'stores', http_request)

    def test_fields(self, params):
        assert params.fields['books'] == {'title'}

    def test_include(self, params):
        assert params.include.tree == {'books': {}}

    def test___repr__(self, params):
        assert repr(params) == (
            '<Parameters fields={params.fields!r}, '
            'include={params.include!r}>'
        ).format(params=params)


class TestFieldsParameter(object):
    def test_missing_fields_parameter(self, resources):
        fields = FieldsParameter(resources, fields=None)
        assert fields['series'] == {'title'}
        assert fields['authors'] == {'name', 'date_of_birth', 'date_of_death'}
        assert fields['books'] == {
            'date_published',
            'title',
            'author',
            'series',
        }
        assert fields['chapters'] == {'title', 'ordering', 'book'}
        assert fields['stores'] == {'name', 'books'}

    def test_invalid_fields_parameter(self, resources):
        with pytest.raises(exc.InvalidFieldFormat):
            FieldsParameter(resources, fields='invalid')

    def test_invalid_resource(self, resources):
        with pytest.raises(exc.InvalidResource) as exc_info:
            FieldsParameter(resources, fields={'invalid': ''})
        assert exc_info.value.type == 'invalid'

    def test_invalid_field(self, resources):
        with pytest.raises(exc.InvalidField) as exc_info:
            FieldsParameter(resources, fields={'series': 'invalid'})
        assert exc_info.value.type == 'series'
        assert exc_info.value.field == 'invalid'

    def test_invalid_field_value(self, resources):
        with pytest.raises(exc.InvalidFieldValue) as exc_info:
            FieldsParameter(resources, fields={'series': ['foo', 'bar']})
        assert exc_info.value.type == 'series'
        assert exc_info.value.value == ['foo', 'bar']

    def test_restricts_fields_to_be_returned(self, resources):
        fields = FieldsParameter(resources, fields={
            'books': 'title,date_published,author',
            'authors': 'name'
        })
        assert fields['books'] == {'title', 'date_published', 'author'}
        assert fields['authors'] == {'name'}

    def test___repr__(self, resources):
        fields = FieldsParameter(resources, fields={'authors': 'name'})
        assert repr(fields) == "<FieldsParameter {'authors': ['name']}>"


class TestIncludeParameter(object):
    @pytest.mark.parametrize(
        ('include', 'tree'),
        [
            ('', {}),
            ('books', {'books': {}}),
            ('books.author', {'books': {'author': {}}}),
            ('books.author,books', {'books': {'author': {}}}),
        ]
    )
    def test_tree(self, resources, include, tree):
        assert IncludeParameter(resources, 'stores', include).tree == tree

    def test_invalid_relationship(self, resources):
        with pytest.raises(exc.InvalidInclude) as exc_info:
            IncludeParameter(resources, 'stores', 'books.invalid')
        assert exc_info.value.type == 'books'
        assert exc_info.value.relationship == 'invalid'

    def test_invalid_value(self, resources):
        with pytest.raises(exc.InvalidIncludeValue) as exc_info:
            IncludeParameter(resources, 'stores', {'foo': 'bar'})
        assert exc_info.value.value == {'foo': 'bar'}

    def test___repr__(self, resources):
        include = IncludeParameter(
            resources,
            type='stores',
            include='books.author,books'
        )
        assert repr(include) == "<IncludeParameter 'books.author,books'>"
