import json

import pytest


@pytest.fixture
def data(fantasy_database):
    return {
        "type": "books",
        "attributes": {
            "title": "The Book of Lost Tales",
            "date_published": "1983-10-28"
        },
        "relationships": {
            "author": {
                "data": {
                    "type": "authors",
                    "id": "1"
                }
            },
            "series": {
                "data": None
            },
            "stores": {
                "data": [
                    {
                        "type": "stores",
                        "id": "1"
                    }
                ]
            }
        }
    }


class TestSuccessfulRequest(object):
    @pytest.fixture
    def create_response(self, client, data):
        return client.post('/books', data=json.dumps({"data": data}))

    @pytest.fixture
    def fetch_response(self, client, create_response):
        url = '/books/{id}'.format(id=create_response.json['data']['id'])
        return client.get(url)

    def test_responds_with_201_status_code(self, create_response):
        assert create_response.status_code == 201

    def test_response_includes_the_created_resource_object(
        self, create_response
    ):
        assert create_response.json['data']['type'] == 'books'
        assert 'id' in create_response.json['data']
        assert 'title' in create_response.json['data']['attributes']

    @pytest.mark.xfail
    def test_response_includes_location_header(self, create_response):
        assert create_response.location == 'http://example.com/books/12'

    @pytest.mark.xfail
    def test_location_header_matches_self_link(self, create_response):
        self_link = create_response.json['links']['self']
        assert self_link == create_response.location

    def test_the_created_resource_can_be_fetched(self, fetch_response):
        assert fetch_response.status_code == 200

    def test_sets_relationships_to_the_created_resource(
        self, data, fetch_response
    ):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['author']['data']['id'] == '1'
        assert relationships['series']['data'] is None
        assert len(relationships['stores']['data']) == 1
        assert relationships['stores']['data'][0]['id'] == '1'

    def test_sets_attributes_to_the_created_resource(
        self, data, fetch_response
    ):
        attributes = fetch_response.json['data']['attributes']
        assert attributes['title'] == 'The Book of Lost Tales'
        assert attributes['date_published'] == '1983-10-28'


class TestInvalidResourceType(object):
    @pytest.fixture
    def response(self, client):
        return client.post('/foobars')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_RESOURCE'


class TestInvalidJSON(object):
    @pytest.fixture
    def response(self, client):
        return client.post('/books', data='invalid')

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_invalid_json_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_JSON'


class TestInvalidRequestBody(object):
    @pytest.fixture
    def response(self, client):
        return client.post('/books', data=json.dumps({}))

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_validation_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'VALIDATION_ERROR'
        assert error['detail'] == "'data' is a required property"
        assert error['source'] == {'pointer': '/'}


class TestConflictingType(object):
    @pytest.fixture
    def response(self, client):
        return client.post('/books', data=json.dumps({
            "data": {
                "type": "authors"
            }
        }))

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_type_mismatch_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'TYPE_MISMATCH'
        assert error['detail'] == "authors does not match the endpoint type."
        assert error['source'] == {'pointer': '/data/type'}


class TestClientGeneratedIDsUnsupported(object):
    @pytest.fixture
    def data(self, data):
        data['id'] = '123'
        return data

    @pytest.fixture
    def response(self, client, data):
        return client.post('/books', data=json.dumps({"data": data}))

    def test_responds_with_403_status_code(self, response):
        assert response.status_code == 403

    def test_returns_client_generated_ids_unsupported_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'CLIENT_GENERATED_IDS_UNSUPPORTED'
        assert error['detail'] == (
            'The server does not support creation of books resource with a '
            'client-generated ID.'
        )
        assert error['source'] == {'pointer': '/data/id'}


class TestSuccessfulRequestWithClientGeneratedID(object):
    @pytest.fixture
    def data(self, fantasy_database):
        return {
            "id": "123",
            "type": "authors",
            "attributes": {
                "name": "George R. R. Martin",
                "date_of_birth": "1948-09-20"
            }
        }

    @pytest.fixture
    def response(self, client, data):
        return client.post('/authors', data=json.dumps({"data": data}))

    def test_responds_with_201_status_code(self, response):
        assert response.status_code == 201

    def test_the_created_resource_has_client_generated_id(self, response):
        assert response.json['data']['id'] == '123'


class TestConflictWhenUsingClientGeneratedID(object):
    @pytest.fixture
    def data(self, fantasy_database):
        return {
            "id": "1",
            "type": "authors",
            "attributes": {
                "name": "George R. R. Martin",
                "date_of_birth": "1948-09-20"
            }
        }

    @pytest.fixture
    def response(self, client, data):
        return client.post('/authors', data=json.dumps({"data": data}))

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_resource_already_exists_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'RESOURCE_ALREADY_EXISTS'
        assert error['detail'] == (
            'A resource with (authors, 1) type-id pair already exists.'
        )
        assert error['source'] == {'pointer': '/data/id'}
