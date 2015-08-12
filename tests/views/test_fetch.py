import pytest


class TestSuccessfulRequest(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_an_array_of_resource_objects(self, response):
        assert len(response.json['data']) == 11


class TestSuccessfulRequestEmptyCollection(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/books')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_an_empty_array(self, response):
        assert response.json['data'] == []


class TestIncludeRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books?include=author')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 2


class TestSparseFieldsets(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books?fields%5Bbooks%5D=title')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_only_requested_fields(self, response):
        first_book = response.json['data'][0]
        assert first_book['attributes'].keys() == ['title']
        assert 'relationships' not in first_book


class TestPagination(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books?page%5Bnumber%5D=3&page%5Bsize%5D=5')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_resource_objects_for_the_requested_page(self, response):
        assert len(response.json['data']) == 1


class TestRequestInvalidResource(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/foobars')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_RESOURCE'
