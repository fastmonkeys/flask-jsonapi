import json

import pytest


class TestUpdatingToOneRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch(
            '/books/1/relationships/series',
            data=json.dumps({
                'data': {
                    'type': 'series',
                    'id': '2'
                }
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/series')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_updates_the_relationship(self, fetch_response):
        assert fetch_response.json['data'] == {
            'type': 'series',
            'id': '2'
        }


class TestRemovingToOneRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch(
            '/books/1/relationships/series',
            data=json.dumps({'data': None})
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/series')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_updates_the_relationship(self, fetch_response):
        assert fetch_response.json['data'] is None


class TestCreateToOneRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.post('/books/1/relationships/author')

    def test_responds_with_405_status_code(self, response):
        assert response.status_code == 405


class TestDeleteToOneRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete('/books/1/relationships/author')

    def test_responds_with_405_status_code(self, response):
        assert response.status_code == 405


class TestUpdateRelationshipWithInvalidJSON(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch('/books/1/relationships/author', data='invalid')

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_invalid_json_error(self, response):
        assert response.json['errors'][0]['title'] == 'Invalid JSON'


class TestUpdateRelationshipWithInvalidRequestBody(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.patch(
            '/books/1/relationships/author',
            data=json.dumps({})
        )

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_validation_error(self, response):
        error = response.json['errors'][0]
        assert error['title'] == 'Validation Error'


class TestUpdatingToManyRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '1'
                    },
                    {
                        'type': 'stores',
                        'id': '2'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_updates_the_relationship(self, fetch_response):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert store_ids == {'1', '2'}


class TestClearingToManyRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.patch(
            '/books/1/relationships/stores',
            data=json.dumps({'data': []})
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_updates_the_relationship(self, fetch_response):
        assert fetch_response.json['data'] == []


class TestRejectFullReplacement(object):
    @pytest.fixture
    def update_response(self, fantasy_database, client):
        return client.patch(
            '/stores/1/relationships/books',
            data=json.dumps({'data': []})
        )

    def test_responds_with_403_status_code(self, update_response):
        assert update_response.status_code == 403

    def test_returns_validation_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['title'] == 'Full Replacement Disallowed'


class TestCreateToManyRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '1'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_adds_the_specified_member_to_relationship(self, fetch_response):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert store_ids == {'1', '2'}


class TestCreateAlreadyPresentToManyRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '2'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_does_add_the_specified_member_again_to_relationship(
        self, fetch_response
    ):
        assert fetch_response.json['data'] == [
            {'type': 'stores', 'id': '2'}
        ]


class TestCreateSameToManyRelationshipTwice(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '1'
                    },
                    {
                        'type': 'stores',
                        'id': '1'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_adds_the_specified_member_once_to_relationship(
        self, fetch_response
    ):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert store_ids == {'1', '2'}


class TestCreateNewAndAlreadyPresentToManyRelationship(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '1'
                    },
                    {
                        'type': 'stores',
                        'id': '2'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, update_response):
        return client.get('/books/1/relationships/stores')

    def test_responds_with_204_status_code(self, update_response):
        assert update_response.status_code == 204

    def test_adds_the_new_member_to_relationship(self, fetch_response):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert store_ids == {'1', '2'}


class TestCreateToManyRelationshipForResourceNotExisting(object):
    @pytest.fixture
    def update_response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'stores',
                        'id': '123'
                    }
                ]
            })
        )

    def test_responds_with_404_status_code(self, update_response):
        assert update_response.status_code == 404

    def test_returns_resource_not_found_error(self, update_response):
        error = update_response.json['errors'][0]
        assert error['title'] == 'Resource Not Found'


class TestCreateToManyRelationshipWithConflictingType(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({
                'data': [
                    {
                        'type': 'authors',
                        'id': '1'
                    }
                ]
            })
        )

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_type_mismatch_error(self, response):
        error = response.json['errors'][0]
        assert error['title'] == 'Type Mismatch'


class TestCreateToManyRelationshipWithInvalidJSON(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.post('/books/1/relationships/stores', data='invalid')

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_invalid_json_error(self, response):
        assert response.json['errors'][0]['title'] == 'Invalid JSON'


class TestCreateToManyRelationshipWithInvalidRequestBody(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.post(
            '/books/1/relationships/stores',
            data=json.dumps({})
        )

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_validation_error(self, response):
        error = response.json['errors'][0]
        assert error['title'] == 'Validation Error'
        assert error['detail'] == '"data" is a required property'
        assert error['source'] == {'pointer': ''}


class TestDeleteToManyRelationship(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete(
            '/stores/2/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'books',
                        'id': '1'
                    },
                    {
                        'type': 'books',
                        'id': '3'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, delete_response):
        return client.get('/stores/2/relationships/books')

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204

    def test_removes_the_specified_members_from_the_relationship(
        self, fetch_response
    ):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert len(data) > 0
        assert len(store_ids & {'1', '3'}) == 0


class TestDeleteToManyRelationshipThatDoesNotExist(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete(
            '/stores/1/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'books',
                        'id': '1'
                    }
                ]
            })
        )

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204


class TestDeleteToManyRelationshipWhenResourceDoesNotExist(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete(
            '/stores/2/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'books',
                        'id': '123'
                    }
                ]
            })
        )

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204


class TestDeletePresentAndNotPresentToManyRelationship(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete(
            '/stores/2/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'books',
                        'id': '123'
                    },
                    {
                        'type': 'books',
                        'id': '1'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, delete_response):
        return client.get('/stores/2/relationships/books')

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204

    def test_removes_the_specified_members_from_the_relationship(
        self, fetch_response
    ):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert len(data) > 0
        assert len(store_ids & {'1', '123'}) == 0


class TestDeleteSameToManyRelationshipTwice(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete(
            '/stores/2/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'books',
                        'id': '1'
                    },
                    {
                        'type': 'books',
                        'id': '1'
                    }
                ]
            })
        )

    @pytest.fixture
    def fetch_response(self, client, delete_response):
        return client.get('/stores/2/relationships/books')

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204

    def test_removes_the_specified_members_from_the_relationship(
        self, fetch_response
    ):
        data = fetch_response.json['data']
        store_ids = {linkage['id'] for linkage in data}
        assert len(data) > 0
        assert len(store_ids & {'1'}) == 0


class TestDeleteToManyRelationshipWithConflictingType(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete(
            '/stores/2/relationships/books',
            data=json.dumps({
                'data': [
                    {
                        'type': 'authors',
                        'id': '1'
                    }
                ]
            })
        )

    def test_responds_with_409_status_code(self, response):
        assert response.status_code == 409

    def test_returns_type_mismatch_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'TypeMismatch'
        assert error['detail'] == (
            'authors is not a valid type for this operation.'
        )
        assert error['source'] == {'pointer': '/data/0/type'}


class TestDeleteToManyRelationshipWithInvalidJSON(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete('/books/1/relationships/stores', data='invalid')

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_invalid_json_error(self, response):
        assert response.json['errors'][0]['code'] == 'InvalidJSON'


class TestDeleteToManyRelationshipWithInvalidRequestBody(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete(
            '/books/1/relationships/stores',
            data=json.dumps({})
        )

    def test_responds_with_400_status_code(self, response):
        assert response.status_code == 400

    def test_returns_validation_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'ValidationError'
        assert error['detail'] == "'data' is a required property"
        assert error['source'] == {'pointer': '/'}
