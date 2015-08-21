import json

import pytest


class TestUpdateAttributes(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch('/books/1', data=json.dumps({
            'data':  {
                'type': 'books',
                'id': '1',
                'attributes': {
                    'title': 'Silmarillion'
                }
            }
        }))

    @pytest.fixture
    def fetch_response(self, update_response, client):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, update_response):
        assert update_response.status_code == 200

    def test_response_includes_representation_of_the_updated_resource(
        self, update_response
    ):
        data = update_response.json['data']
        assert data['id'] == '1'
        assert data['type'] == 'books'
        assert data['attributes']['title'] == 'Silmarillion'

    def test_does_not_update_missing_attributes(self, fetch_response):
        attributes = fetch_response.json['data']['attributes']
        assert attributes['date_published'] == '1954-07-29'

    def test_updates_provided_attributes(self, fetch_response):
        attributes = fetch_response.json['data']['attributes']
        assert attributes['title'] == 'Silmarillion'


class TestMissingType(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch('/books/1', data=json.dumps({
            'data':  {
                'id': '1',
                'attributes': {
                    'title': 'Silmarillion'
                }
            }
        }))

    def test_responds_with_400_status_code(self, update_response):
        assert update_response.status_code == 400

    def test_returns_validation_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['code'] == 'ValidationError'
        assert error['detail'] == "'type' is a required property"
        assert error['source'] == {'pointer': '/data'}


class TestMissingId(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/books/1', data=json.dumps({
            'data': {
                'type': 'books',
                'attributes': {
                    'title': 'Silmarillion'
                }
            }
        }))

    def test_responds_with_400_status_code(self, update_response):
        assert update_response.status_code == 400

    def test_returns_validation_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['code'] == 'ValidationError'
        assert error['detail'] == "'id' is a required property"
        assert error['source'] == {'pointer': '/data'}


class TestResourceTypeNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/foobars/1')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_resource_type_not_found_error(self, response):
        assert response.json['errors'][0]['code'] == 'ResourceTypeNotFound'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/123123')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'ResourceNotFound'
        assert error['detail'] == (
            "The resource identified by (books, 123123) type-id pair "
            "could not be found."
        )


class TestInvalidJSON(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/1', data='invalid')

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_invalid_json_error(self, response):
        assert response.json['errors'][0]['code'] == 'InvalidJSON'


class TestInvalidRequestBody(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/1', data=json.dumps({}))

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_validation_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'ValidationError'
        assert error['detail'] == "'data' is a required property"
        assert error['source'] == {'pointer': '/'}


class TestConflictingType(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/1', data=json.dumps({
            "data": {
                "type": "authors",
                "id": "1"
            }
        }))

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_type_mismatch_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'TypeMismatch'
        assert error['detail'] == (
            'authors is not a valid type for this operation.'
        )
        assert error['source'] == {'pointer': '/data/type'}


class TestConflictingID(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/1', data=json.dumps({
            "data": {
                "type": "books",
                "id": "2"
            }
        }))

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_type_mismatch_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'IDMismatch'
        assert error['detail'] == '2 does not match the endpoint id.'
        assert error['source'] == {'pointer': '/data/id'}


class TestUpdateToOneRelationship(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/books/1', data=json.dumps({
            'data': {
                'type': 'books',
                'id': '1',
                'relationships': {
                    'author': {
                        'data': {
                            'type': 'authors',
                            'id': '2'
                        }
                    }
                }
            }
        }))

    @pytest.fixture
    def fetch_response(self, update_response, client):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, update_response):
        assert update_response.status_code == 200

    def test_response_includes_representation_of_the_updated_resource(
        self, update_response
    ):
        data = update_response.json['data']
        assert data['id'] == '1'
        assert data['type'] == 'books'
        assert data['relationships']['author']['data'] == {
            'type': 'authors',
            'id': '2'
        }

    def test_does_not_update_missing_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['series']['data'] == {'type': 'series', 'id': '1'}
        assert len(relationships['chapters']['data']) == 22
        assert len(relationships['stores']['data']) == 1

    def test_updates_provided_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['author']['data'] == {
            'type': 'authors',
            'id': '2'
        }


class TestRemoveToOneRelationship(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/books/1', data=json.dumps({
            'data': {
                'type': 'books',
                'id': '1',
                'relationships': {
                    'series': {
                        'data': None
                    }
                }
            }
        }))

    @pytest.fixture
    def fetch_response(self, update_response, client):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, update_response):
        assert update_response.status_code == 200

    def test_response_includes_representation_of_the_updated_resource(
        self, update_response
    ):
        data = update_response.json['data']
        assert data['id'] == '1'
        assert data['type'] == 'books'
        assert data['relationships']['series']['data'] is None

    def test_does_not_update_missing_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['author']['data'] == {
            'type': 'authors',
            'id': '1'
        }
        assert len(relationships['chapters']['data']) == 22
        assert len(relationships['stores']['data']) == 1

    def test_updates_provided_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['series']['data'] is None


class TestUpdateToManyRelationship(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/books/1', data=json.dumps({
            'data': {
                'type': 'books',
                'id': '1',
                'relationships': {
                    'stores': {
                        'data': [
                            {
                                'type': 'stores',
                                'id': '1'
                            },
                            {
                                'type': 'stores',
                                'id': '2'
                            },
                        ]
                    }
                }
            }
        }))

    @pytest.fixture
    def fetch_response(self, update_response, client):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, update_response):
        assert update_response.status_code == 200

    def test_response_includes_representation_of_the_updated_resource(
        self, update_response
    ):
        data = update_response.json['data']
        assert data['id'] == '1'
        assert data['type'] == 'books'

        store_ids = {
            linkage['id']
            for linkage in data['relationships']['stores']['data']
        }
        assert store_ids == {'1', '2'}

    def test_does_not_update_missing_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['author']['data'] == {
            'type': 'authors',
            'id': '1'
        }
        assert relationships['series']['data'] == {
            'type': 'series',
            'id': '1'
        }
        assert len(relationships['chapters']['data']) == 22

    def test_updates_provided_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        store_ids = {
            linkage['id']
            for linkage in relationships['stores']['data']
        }
        assert store_ids == {'1', '2'}


class TestClearToManyRelationship(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/books/1', data=json.dumps({
            'data': {
                'type': 'books',
                'id': '1',
                'relationships': {
                    'stores': {
                        'data': []
                    }
                }
            }
        }))

    @pytest.fixture
    def fetch_response(self, update_response, client):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, update_response):
        assert update_response.status_code == 200

    def test_response_includes_representation_of_the_updated_resource(
        self, update_response
    ):
        data = update_response.json['data']
        assert data['id'] == '1'
        assert data['type'] == 'books'
        assert data['relationships']['stores']['data'] == []

    def test_does_not_update_missing_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['author']['data'] == {
            'type': 'authors',
            'id': '1'
        }
        assert relationships['series']['data'] == {
            'type': 'series',
            'id': '1'
        }
        assert len(relationships['chapters']['data']) == 22

    def test_updates_provided_relationships(self, fetch_response):
        relationships = fetch_response.json['data']['relationships']
        assert relationships['stores']['data'] == []


class TestRejectFullReplacement(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch('/stores/1', data=json.dumps({
            'data': {
                'type': 'stores',
                'id': '1',
                'relationships': {
                    'books': {
                        'data': []
                    }
                }
            }
        }))

    def test_responds_with_403_status_code(self, update_response):
        assert update_response.status_code == 403

    def test_returns_validation_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['code'] == 'FullReplacementDisallowed'
        assert error['detail'] == "Full replacement of books is not allowed."
        assert error['source'] == {'pointer': '/data/relationships/books'}


class TestReferencingRelatedResourceThatDoesNotExist(object):
    @pytest.fixture
    def data(self, fantasy_database):
        return {
            'type': 'books',
            'id': '1',
            'relationships': {
                'stores': {
                    'data': [
                        {
                            'type': 'stores',
                            'id': '1'
                        },
                        {
                            'type': 'stores',
                            'id': '123123'
                        }
                    ]
                }
            }
        }

    @pytest.fixture
    def update_response(self, client, data):
        return client.patch('/books/1', data=json.dumps({'data': data}))

    def test_responds_with_404_status_code(self, update_response):
        assert update_response.status_code == 404

    def test_returns_resource_not_found_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['code'] == 'ResourceNotFound'
        assert error['detail'] == (
            "The resource identified by (stores, 123123) type-id pair "
            "could not be found."
        )
        assert error['source'] == {
            'pointer': '/data/relationships/stores/data/1'
        }
