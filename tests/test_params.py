import pytest

from flask_jsonapi import exc
from flask_jsonapi.params import FieldsParameter, IncludeParameter


class TestFieldsParameter(object):
    def test_missing_fields_parameter(self, resources):
        fields = FieldsParameter(resources, fields=None)
        assert fields['series'] == {'title'}
        assert fields['authors'] == {
            'books',
            'date_of_birth',
            'date_of_death',
            'name',
        }
        assert fields['books'] == {
            'author',
            'chapters',
            'date_published',
            'series',
            'title',
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
