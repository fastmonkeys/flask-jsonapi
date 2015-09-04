import datetime

import pytest

from flask_jsonapi import errors
from flask_jsonapi.request_parser import RequestParser


@pytest.fixture
def resource(resource_registry):
    return resource_registry.by_type['books']


class TestParse(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_must_be_an_object(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse(data='foobar')
        assert excinfo.value.detail == "'foobar' is not of type 'object'"
        assert excinfo.value.source_pointer == '/'

    def test_must_have_data_member(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse(data={})
        assert excinfo.value.detail == "'data' is a required property"
        assert excinfo.value.source_pointer == '/'

    def test_valid_top_level_document(self, parser):
        result = parser.parse(
            data={
                'data': {
                    'type': 'books',
                    'attributes': {
                        'title': 'The Hobbit',
                        'date_published': '1937-09-21'
                    },
                    'relationships': {
                        'author': {
                            'data': None
                        }
                    }
                }
            }
        )
        assert result.id is None
        assert len(result.fields) == 3
        assert result.fields['title'] == 'The Hobbit'


class TestParseResourceObject(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    @pytest.fixture
    def resource_object(self):
        return {
            'type': 'books',
            'attributes': {
                'title': 'The Hobbit',
                'date_published': '1937-09-21'
            },
            'relationships': {
                'author': {
                    'data': {
                        'type': 'authors',
                        'id': '1'
                    }
                }
            }
        }

    def test_must_be_an_object(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_resource_object(
                data='foobar',
                path=[]
            )
        assert excinfo.value.detail == "'foobar' is not of type 'object'"
        assert excinfo.value.source_pointer == '/'

    def test_must_have_type_member(self, parser, resource_object):
        del resource_object['type']
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_resource_object(
                data=resource_object,
                path=[]
            )
        assert excinfo.value.detail == "'type' is a required property"
        assert excinfo.value.source_pointer == '/'

    def test_type_must_be_a_string(self, parser, resource_object):
        resource_object['type'] = 123
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_resource_object(
                data=resource_object,
                path=[]
            )
        assert excinfo.value.detail == "123 is not of type 'string'"
        assert excinfo.value.source_pointer == '/type'

    def test_id_must_be_a_string(self, parser, resource_object):
        resource_object['id'] = 123
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_resource_object(
                data=resource_object,
                path=[]
            )
        assert excinfo.value.detail == "123 is not of type 'string'"
        assert excinfo.value.source_pointer == '/id'

    def test_returns_parsed_fields(
        self,
        parser,
        resource_object,
        fantasy_database
    ):
        result = parser.parse_resource_object(
            data=resource_object,
            path=[]
        )
        assert len(result.fields) == 3
        assert result.fields['title'] == 'The Hobbit'
        assert result.fields['date_published'] == datetime.date(1937, 9, 21)
        assert result.fields['author'].name == 'J. R. R. Tolkien'

    def test_returns_none_for_id_if_missing(
        self,
        parser,
        resource_object,
        fantasy_database
    ):
        result = parser.parse_resource_object(
            data=resource_object,
            path=[]
        )
        assert result.id is None


class TestParseResourceObjectForUpdate(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource, id='123')

    def test_must_have_id_member(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_resource_object(
                data={'type': 'books'},
                path=[]
            )
        assert excinfo.value.detail == "'id' is a required property"
        assert excinfo.value.source_pointer == '/'


class TestParseAttributesObject(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_must_be_an_object(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_attributes_object(
                data='foobar',
                path=['data', 'attributes']
            )
        assert excinfo.value.detail == "'foobar' is not of type 'object'"
        assert excinfo.value.source_pointer == '/data/attributes'

    def test_must_include_required_attributes(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_attributes_object(
                data={},
                path=['data', 'attributes']
            )
        assert excinfo.value.detail == "'date_published' is a required field"

    def test_may_include_known_attributes(self, parser):
        attributes = parser.parse_attributes_object(
            data={
                'title': 'The Hobbit',
                'date_published': '1937-09-21'
            },
            path=['data', 'attributes']
        )
        assert attributes == {
            'title': 'The Hobbit',
            'date_published': datetime.date(1937, 9, 21)
        }

    def test_must_not_include_unknown_members(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_attributes_object(
                data={
                    'title': 'The Hobbit',
                    'date_published': '1937-09-21',
                    'foo': 'bar'
                },
                path=['data', 'attributes']
            )
        assert excinfo.value.detail == (
            "'foo' is not a valid attribute for 'books' resource"
        )
        assert excinfo.value.source_pointer == '/data/attributes/foo'


class TestParseAttributesObjectForUpdate(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource, id='123')

    def test_may_not_include_required_attributes(self, parser):
        attributes = parser.parse_attributes_object(
            data={},
            path=['data', 'attributes']
        )
        assert attributes == {}


class TestParseRelationshipsObject(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_must_be_an_object(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_relationships_object(
                data='foobar',
                path=['data', 'relationships']
            )
        assert excinfo.value.detail == "'foobar' is not of type 'object'"
        assert excinfo.value.source_pointer == '/data/relationships'

    def test_must_include_required_relationships(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_relationships_object(
                data={},
                path=['data', 'relationships']
            )
        assert excinfo.value.detail == "'author' is a required field"

    def test_must_not_include_unknown_members(self, parser):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_relationships_object(
                data={
                    'foo': {
                        'data': None
                    }
                },
                path=['data', 'relationships']
            )
        assert excinfo.value.detail == (
            "'foo' is not a valid relationship for 'books' resource"
        )
        assert excinfo.value.source_pointer == '/data/relationships/foo'

    def test_may_include_to_one_relationships(
        self,
        parser,
        models,
        fantasy_database
    ):
        relationships = parser.parse_relationships_object(
            data={
                'author': {
                    'data': {
                        'type': 'authors',
                        'id': '1'
                    }
                }
            },
            path=['data', 'relationships']
        )
        author = relationships['author']
        assert isinstance(author, models.Author)
        assert author.id == 1

    def test_may_include_to_many_relationships(
        self,
        parser,
        models,
        fantasy_database
    ):
        relationships = parser.parse_relationships_object(
            data={
                'author': {
                    'data': None
                },
                'chapters': {
                    'data': [
                        {
                            'type': 'chapters',
                            'id': '1'
                        },
                        {
                            'type': 'chapters',
                            'id': '2'
                        },
                    ]
                }
            },
            path=['data', 'relationships']
        )
        chapters = relationships['chapters']
        assert len(chapters) == 2
        assert isinstance(chapters[0], models.Chapter)
        assert chapters[0].id == 1


class TestParseRelationshipsObjectForUpdate(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource, id='123')

    def test_may_not_include_required_relationships(self, parser):
        relationships = parser.parse_relationships_object(
            data={},
            path=['data', 'relationships']
        )
        assert relationships == {}


class TestParseRelationshipObjectWithToOneRelationship(object):
    @pytest.fixture
    def relationship(self, resource):
        return resource.relationships['author']

    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_must_be_an_object(self, parser, relationship):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_relationship_object(
                relationship=relationship,
                data='foobar',
                path=[]
            )
        assert excinfo.value.detail == "'foobar' is not of type 'object'"
        assert excinfo.value.source_pointer == '/'

    def test_must_have_data(self, parser, relationship):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser.parse_relationship_object(
                relationship=relationship,
                data={},
                path=[]
            )
        assert excinfo.value.detail == "'data' is a required property"
        assert excinfo.value.source_pointer == '/'

    def test_data_may_be_null(self, parser, relationship):
        author = parser.parse_relationship_object(
            relationship=relationship,
            data={
                "data": None
            },
            path=[]
        )
        assert author is None

    def test_data_may_be_a_linkage_object(
        self,
        parser,
        relationship,
        models,
        fantasy_database
    ):
        author = parser.parse_relationship_object(
            relationship=relationship,
            data={
                "data": {
                    "type": "authors",
                    "id": "1"
                }
            },
            path=[]
        )
        assert isinstance(author, models.Author)
        assert author.id == 1


class TestParseRelationshipObjectWithToManyRelationship(object):
    @pytest.fixture
    def relationship(self, resource):
        return resource.relationships['chapters']

    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_data_may_be_an_empty_array(self, parser, relationship):
        chapters = parser.parse_relationship_object(
            relationship=relationship,
            data={
                "data": []
            },
            path=[]
        )
        assert chapters == []

    def test_data_may_be_an_array_of_linkage_objects(
        self,
        parser,
        relationship,
        fantasy_database,
        models
    ):
        chapters = parser.parse_relationship_object(
            relationship=relationship,
            data={
                "data": [
                    {'type': 'chapters', 'id': '1'},
                    {'type': 'chapters', 'id': '2'},
                ]
            },
            path=[]
        )
        assert len(chapters) == 2
        assert isinstance(chapters[0], models.Chapter)
        assert chapters[0].id == 1


class TestParseResourceIdentifierObject(object):
    @pytest.fixture
    def parser(self, resource):
        return RequestParser(resource)

    def test_must_have_type(self, parser, resource):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser._parse_resource_identifier(
                resource=resource,
                data={'id': '1'},
                path=[]
            )
        assert excinfo.value.detail == "'type' is a required property"
        assert excinfo.value.source_pointer == '/'

    def test_must_have_id(self, parser, resource):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser._parse_resource_identifier(
                resource=resource,
                data={'type': 'books'},
                path=[]
            )
        assert excinfo.value.detail == "'id' is a required property"
        assert excinfo.value.source_pointer == '/'

    def test_type_must_be_a_string(self, parser, resource):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser._parse_resource_identifier(
                resource=resource,
                data={'type': 123, 'id': '123'},
                path=[]
            )
        assert excinfo.value.detail == "123 is not of type 'string'"
        assert excinfo.value.source_pointer == '/type'

    def test_id_must_be_a_string(self, parser, resource):
        with pytest.raises(errors.ValidationError) as excinfo:
            parser._parse_resource_identifier(
                resource=resource,
                data={'type': 'books', 'id': 123},
                path=[]
            )
        assert excinfo.value.detail == "123 is not of type 'string'"
        assert excinfo.value.source_pointer == '/id'
