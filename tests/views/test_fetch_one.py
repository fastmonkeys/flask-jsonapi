import pytest


class TestFetchOne(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_resource(self, response):
        assert response.json['data']['type'] == 'books'
        assert response.json['data']['id'] == '1'

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/123123')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_resource_not_found_error(self, response):
        assert response.json['errors'][0]['title'] == 'Resource Not Found'


class TestIncludeRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1?include=author')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 1

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1?include=author'


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

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == (
            'http://example.com/books/1?fields%5Bbooks%5D=title'
        )
