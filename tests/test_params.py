import pytest

from flask_jsonapi import exc
from flask_jsonapi.params import FieldsParameter


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
