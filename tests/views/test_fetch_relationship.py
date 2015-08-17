import pytest


class TestFetchToOneRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/relationships/author')

    def test_response_has_correct_content_type(self, response):
        assert response.content_type == 'application/vnd.api+json'

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1/relationships/author'

    @pytest.mark.xfail
    def test_response_contains_related_link(self, response):
        related_link = response.json['links']['self']
        assert related_link == 'http://example.com/books/1/author'

    def test_response_contains_appropriate_resource_linkage(self, response):
        assert response.json['data'] == {
            'type': 'authors',
            'id': '1'
        }


class TestFetchEmptyToOneRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/11/relationships/series')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_response_contains_appropriate_resource_linkage(self, response):
        assert response.json['data'] is None


class TestFetchToManyRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/relationships/chapters')

    def test_response_has_correct_content_type(self, response):
        assert response.content_type == 'application/vnd.api+json'

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1/relationships/chapters'

    @pytest.mark.xfail
    def test_response_contains_related_link(self, response):
        related_link = response.json['links']['self']
        assert related_link == 'http://example.com/books/1/chapters'

    def test_response_contains_appropriate_resource_linkage(self, response):
        data = response.json['data']
        assert len(data) == 20
        assert data[0] == {
            'type': 'chapters',
            'id': '1'
        }


class TestFetchToManyRelationshipWithPagination(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/relationships/chapters?page%5Bnumber%5D=2')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_response_contains_linkages_for_the_requested_page(self, response):
        assert len(response.json['data']) == 2


class TestFetchEmptyToManyRelationship(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/1/relationships/books')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_response_contains_appropriate_resource_linkage(self, response):
        assert response.json['data'] == []


class TestInvalidResourceType(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/foobars/1/relationships/author')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'INVALID_RESOURCE'
        assert error['detail'] == 'foobars is not a valid resource'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/123123/relationships/author')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'RESOURCE_NOT_FOUND'
        assert error['detail'] == (
            "The resource identified by (books, 123123) type-id pair "
            "could not be found."
        )


class TestInvalidRelationship(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/books/1/relationships/foobar')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        error = response.json['errors'][0]
        assert error['code'] == 'RELATIONSHIP_NOT_FOUND'
        assert error['detail'] == (
            'foobar is not a valid relationship for books.'
        )
