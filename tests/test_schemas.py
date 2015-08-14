import jsonschema
import pytest

from flask_jsonapi import errors, schemas


class TestCreateRequestValidation(object):
    @pytest.fixture
    def resource(self, resources):
        return resources.by_type['books']

    @pytest.fixture
    def schema(self, resource):
        return schemas.get_create_request_schema(resource)

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

    def test_data_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({'data': 'foobar'}, schema)
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == ['data']

    def test_data_must_have_type_member(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate({'data': {}}, schema)
        assert excinfo.value.message == "'type' is a required property"
        assert list(excinfo.value.path) == ['data']

    def test_type_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {'data': {'type': 123}},
                schema
            )
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['data', 'type']

    def test_id_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {'data': {'type': 'books', 'id': 123}},
                schema
            )
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == ['data', 'id']

    def test_attributes_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {'data': {'type': 'books', 'attributes': 'foobar'}},
                schema
            )
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == ['data', 'attributes']

    def test_attributes_can_include_known_attributes(self, schema):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'attributes': {
                        'title': 'The Hobbit'
                    }
                }
            },
            schema
        )

    def test_attributes_must_not_include_unknown_members(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'attributes': {
                            'foo': 'bar'
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == (
            "Additional properties are not allowed ('foo' was unexpected)"
        )
        assert list(excinfo.value.path) == ['data', 'attributes']

    def test_relationships_must_be_an_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {'data': {'type': 'books', 'relationships': 'foobar'}},
                schema
            )
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == ['data', 'relationships']

    def test_relationship_must_be_on_object(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': 'foobar'
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "'foobar' is not of type 'object'"
        assert list(excinfo.value.path) == ['data', 'relationships', 'author']

    def test_relationships_must_not_include_unknown_members(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'foo': {
                                'data': None
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == (
            "Additional properties are not allowed ('foo' was unexpected)"
        )
        assert list(excinfo.value.path) == ['data', 'relationships']

    def test_relationship_must_have_data(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': {}
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "'data' is a required property"
        assert list(excinfo.value.path) == ['data', 'relationships', 'author']

    def test_to_one_relationship_data_can_be_null(self, schema):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'relationships': {
                        'author': {
                            "data": None
                        }
                    }
                }
            },
            schema
        )

    def test_to_one_relationship_data_can_be_a_linkage_object(self, schema):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'relationships': {
                        'author': {
                            "data": {
                                "type": "authors",
                                "id": "1"
                            }
                        }
                    }
                }
            },
            schema
        )

    def test_to_one_relationship_data_cannot_be_an_array(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': {
                                "data": []
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "[] is not of type 'null', 'object'"
        assert list(excinfo.value.path) == [
            'data',
            'relationships',
            'author',
            'data'
        ]

    def test_to_many_relationship_data_can_be_an_empty_array(self, schema):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'relationships': {
                        'chapters': {
                            "data": []
                        }
                    }
                }
            },
            schema
        )

    def test_to_many_relationship_data_can_be_an_array_of_linkage_objects(
        self, schema
    ):
        jsonschema.validate(
            {
                'data': {
                    'type': 'books',
                    'relationships': {
                        'chapters': {
                            'data': [
                                {'type': 'chapters', 'id': '1'},
                                {'type': 'chapters', 'id': '2'},
                            ]
                        }
                    }
                }
            },
            schema
        )

    def test_to_many_relationship_data_cannot_be_null(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'chapters': {
                                "data": None
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "None is not of type 'array'"
        assert list(excinfo.value.path) == [
            'data',
            'relationships',
            'chapters',
            'data'
        ]

    def test_linkage_must_have_type_and_id(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': {
                                "data": {}
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "'type' is a required property"
        assert list(excinfo.value.path) == [
            'data',
            'relationships',
            'author',
            'data'
        ]

    def test_linkage_type_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': {
                                "data": {
                                    "type": 123,
                                    "id": "123"
                                }
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == [
            'data',
            'relationships',
            'author',
            'data',
            'type'
        ]

    def test_linkage_id_must_be_a_string(self, schema):
        with pytest.raises(jsonschema.ValidationError) as excinfo:
            jsonschema.validate(
                {
                    'data': {
                        'type': 'books',
                        'relationships': {
                            'author': {
                                "data": {
                                    "type": "authors",
                                    "id": 123
                                }
                            }
                        }
                    }
                },
                schema
            )
        assert excinfo.value.message == "123 is not of type 'string'"
        assert list(excinfo.value.path) == [
            'data',
            'relationships',
            'author',
            'data',
            'id'
        ]
