import pytest


@pytest.fixture(params=[
    'flask_jsonapi.controllers.default.DefaultController',
    'flask_jsonapi.controllers.postgresql.PostgreSQLController',
])
def controller_class(request):
    return request.param


class TestSuccessfulRequest(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_requested_resource(self, response):
        assert response.json['data']['type'] == 'books'
        assert response.json['data']['id'] == '1'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/123123')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_resource_not_found_error(self, response):
        assert response.json['errors'][0]['code'] == 'RESOURCE_NOT_FOUND'


class TestIncludeRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1?include=author')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 1


class TestSparseFieldsets(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1?fields%5Bbooks%5D=title')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_only_requested_fields(self, response):
        book = response.json['data']
        assert list(book['attributes'].keys()) == ['title']
        assert 'relationships' not in book


class TestRequestInvalidResource(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/foobars/1')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_RESOURCE'
