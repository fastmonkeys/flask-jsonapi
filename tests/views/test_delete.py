import pytest


class TestSuccessfulRequest(object):
    @pytest.fixture
    def delete_response(self, client, fantasy_database):
        return client.delete('/books/1')

    @pytest.fixture
    def fetch_response(self, client, delete_response):
        return client.get('/books/1')

    def test_responds_with_204_status_code(self, delete_response):
        assert delete_response.status_code == 204

    def test_responds_with_empty_body(self, delete_response):
        assert delete_response.data == ''

    def test_deletes_the_resource(self, fetch_response):
        assert fetch_response.status_code == 404


class TestInvalidResourceType(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete('/foobars/1')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_RESOURCE'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.delete('/books/123')

    def test_responds_with_204_status_code(self, response):
        assert response.status_code == 204
