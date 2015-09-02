import jsonschema
import pytest

from flask_jsonapi import schemas


@pytest.fixture
def resource(resource_registry):
    return resource_registry.by_type['books']


class TestTopLevelSchema(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_top_level_schema(resource, for_update=False)

    def test_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate('foobar', schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == []

    def test_must_have_data_member(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({}, schema)
        assert excinfo.value.message == "'data' is a required property"
        assert list(excinfo.value.path) == []

    def test_valid_top_level_document(self, schema):
        jsonschema.validate(
            {
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
            },
            schema
        )


class TestTopLevelSchemaForUpdate(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_top_level_schema(resource, for_update=True)

    def test_valid_top_level_document(self, schema):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'id': '123'
                }
            },
            schema
        )


class TestResourceObjectSchema(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_resource_object_schema(resource, for_update=False)

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
                    'data': None
                }
            }
        }

    def test_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate('foobar', schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == []

    def test_must_have_type_member(self, schema, resource_object):
        del resource_object['type']
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(resource_object, schema)
        assert excinfo.value.message == "'type' is a required property"
        assert list(excinfo.value.path) == []

    def test_type_must_be_a_string(self, schema, resource_object):
        resource_object['type'] = 123
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(resource_object, schema)
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['type']

    def test_id_must_be_a_string(self, schema, resource_object):
        resource_object['id'] = 123
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(resource_object, schema)
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['id']

    def test_must_have_required_attributes(self, schema, resource_object):
        del resource_object['attributes']
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(resource_object, schema)
        assert excinfo.value.message == "'attributes' is a required property"
        assert list(excinfo.value.path) == []

    def test_must_have_required_relationships(self, schema, resource_object):
        del resource_object['relationships']
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(resource_object, schema)
        assert excinfo.value.message == (
            "'relationships' is a required property"
        )
        assert list(excinfo.value.path) == []


class TestResourceObjectSchemaForUpdate(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_resource_object_schema(resource, for_update=True)

    def test_must_have_id_member(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({'type': 'books'}, schema)
        assert excinfo.value.message == "'id' is a required property"
        assert list(excinfo.value.path) == []

    def test_may_not_include_required_fields(self, schema):
        jsonschema.validate({'type': 'books', 'id': '1'}, schema)


class TestAttributesObjectSchema(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_attributes_object_schema(resource, for_update=False)

    def test_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate('foobar', schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == []

    def test_must_include_required_attributes(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({}, schema)
        assert excinfo.value.message == (
            "'date_published' is a required property"
        )

    def test_may_include_known_attributes(self, schema):
        jsonschema.validate(
            {
                'title': 'The Hobbit',
                'date_published': '1937-09-21'
            },
            schema
        )

    def test_must_not_include_unknown_members(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'title': 'The Hobbit',
                    'date_published': '1937-09-21',
                    'foo': 'bar'
                },
                schema
            )
        assert excinfo.value.message == (
            "Additional properties are not allowed ('foo' was unexpected)"
        )
        assert list(excinfo.value.path) == []


class TestAttributesObjectSchemaForUpdate(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_attributes_object_schema(resource, for_update=True)

    def test_may_not_include_required_attributes(self, schema):
        jsonschema.validate({}, schema)


class TestRelationshipsObjectSchema(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_relationships_object_schema(
            resource,
            for_update=False
        )

    def test_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate('foobar', schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == []

    def test_must_not_include_unknown_members(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'foo': {
                        'data': None
                    }
                },
                schema
            )
        assert excinfo.value.message == (
            "Additional properties are not allowed ('foo' was unexpected)"
        )
        assert list(excinfo.value.path) == []

    def test_must_include_required_relationships(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({}, schema)
        assert excinfo.value.message == "'author' is a required property"

    def test_may_include_to_one_relationships(self, schema):
        jsonschema.validate(
            {
                'author': {
                    'data': {
                        'type': 'authors',
                        'id': '123'
                    }
                }
            },
            schema
        )

    def test_may_include_to_many_relationships(self, schema):
        jsonschema.validate(
            {
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
            schema
        )


class TestRelationshipsObjectSchemaForUpdate(object):
    @pytest.fixture
    def schema(self, resource):
        return schemas.get_relationships_object_schema(
            resource,
            for_update=True
        )

    def test_may_not_include_required_relationships(self, schema):
        jsonschema.validate({}, schema)


class TestToOneRelationshipObjectSchema(object):
    @pytest.fixture
    def relationship(self, resource):
        return resource.relationships['author']

    @pytest.fixture
    def schema(self, relationship):
        return schemas.get_relationship_object_schema(relationship)

    def test_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate('foobar', schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == []

    def test_must_have_data(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({}, schema)
        assert excinfo.value.message == "'data' is a required property"
        assert list(excinfo.value.path) == []

    def test_data_may_be_null(self, schema):
        jsonschema.validate({"data": None}, schema)

    def test_data_may_be_a_linkage_object(self, schema):
        jsonschema.validate(
            {
                "data": {
                    "type": "authors",
                    "id": "1"
                }
            },
            schema
        )

    def test_data_cannot_be_an_array(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    "data": []
                },
                schema
            )
        assert excinfo.value.message == "[] is not of type 'object', 'null'"
        assert list(excinfo.value.path) == ['data']


class TestToManyRelationshipObjectSchema(object):
    @pytest.fixture
    def relationship(self, resource):
        return resource.relationships['chapters']

    @pytest.fixture
    def schema(self, relationship):
        return schemas.get_relationship_object_schema(relationship)

    def test_data_may_be_an_empty_array(self, schema):
        jsonschema.validate(
            {
                "data": []
            },
            schema
        )

    def test_data_may_be_an_array_of_linkage_objects(self, schema):
        jsonschema.validate(
            {
                'data': [
                    {'type': 'chapters', 'id': '1'},
                    {'type': 'chapters', 'id': '2'},
                ]
            },
            schema
        )

    def test_data_cannot_be_null(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    "data": None
                },
                schema
            )
        assert excinfo.value.message == "None is not of type 'array'"
        assert list(excinfo.value.path) == ['data']


class TestResourceIdentifierObjectSchema(object):
    @pytest.fixture
    def schema(self):
        return schemas.get_resource_identifier_object_schema()

    def test_must_have_type(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({'id': '1'}, schema)
        assert excinfo.value.message == "'type' is a required property"
        assert list(excinfo.value.path) == []

    def test_must_have_id(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({'type': 'books'}, schema)
        assert excinfo.value.message == "'id' is a required property"
        assert list(excinfo.value.path) == []

    def test_type_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({"type": 123, "id": "123"}, schema)
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['type']

    def test_id_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({"type": "authors", "id": 123}, schema)
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['id']
