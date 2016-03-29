import pytest


class TestFetchRelatedToOneRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/author')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_the_requested_resource(self, response):
        data = response.json['data']
        assert data['type'] == 'authors'
        assert data['id'] == '1'

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1/author'


class TestFetchRelatedEmptyToOneRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/11/series')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_the_requested_resource(self, response):
        assert response.json['data'] is None


class TestFetchRelatedToManyRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/chapters')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['data']) == 20

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1/chapters'


class TestFetchRelatedEmptyToManyRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/1/books')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_an_empty_array(self, response):
        assert response.json['data'] == []


class TestToOneRelationWithIncludedRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/author?include=books')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 4

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books/1/author?include=books'


class TestToManyRelationWithIncludedRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/2/books?include=author')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 2

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/stores/2/books?include=author'


class TestToOneRelationWithSparseFieldsets(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/author?fields%5Bauthors%5D=name')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_only_requested_fields(self, response):
        author = response.json['data']
        assert list(author['attributes'].keys()) == ['name']
        assert 'relationships' not in author

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == (
            'http://example.com/books/1/author?fields%5Bauthors%5D=name'
        )


class TestToManyRelationWithSparseFieldsets(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/2/books?fields%5Bbooks%5D=title')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_only_requested_fields(self, response):
        book = response.json['data'][0]
        assert list(book['attributes'].keys()) == ['title']
        assert 'relationships' not in book

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == (
            'http://example.com/stores/2/books?fields%5Bbooks%5D=title'
        )


class TestToManyRelationPagination(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get(
            '/stores/2/books?page%5Bnumber%5D=3&page%5Bsize%5D=5'
        )

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_resource_objects_for_the_requested_page(self, response):
        assert len(response.json['data']) == 2

    @pytest.mark.xfail
    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == (
            'http://example.com/stores/2/books?'
            'page%5Bnumber%5D=3&page%5Bsize%5D=5'
        )

    @pytest.mark.xfail
    def test_response_contains_first_link(first, response):
        first_link = response.json['links']['first']
        assert first_link == (
            'http://example.com/stores/2/books?'
            'page%5Bnumber%5D=1&page%5Bsize%5D=5'
        )

    @pytest.mark.xfail
    def test_response_contains_prev_link(prev, response):
        prev_link = response.json['links']['prev']
        assert prev_link == (
            'http://example.com/stores/2/books?'
            'page%5Bnumber%5D=2&page%5Bsize%5D=5'
        )

    @pytest.mark.xfail
    def test_response_contains_next_link(next, response):
        next_link = response.json['links']['next']
        assert next_link is None

    @pytest.mark.xfail
    def test_response_contains_last_link(last, response):
        last_link = response.json['links']['last']
        assert last_link == (
            'http://example.com/stores/2/books?'
            'page%5Bnumber%5D=3&page%5Bsize%5D=5'
        )


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/123123/chapters')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['title'] == 'Resource Not Found'
