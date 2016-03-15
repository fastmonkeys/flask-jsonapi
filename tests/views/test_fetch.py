import pytest


@pytest.fixture(params=[
    'flask_jsonapi.controllers.default.DefaultController',
    # 'flask_jsonapi.controllers.postgresql.PostgreSQLController',
])
def controller_class(request):
    return request.param


class TestFetch(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_an_array_of_resource_objects(self, response):
        assert len(response.json['data']) == 11

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books'


class TestFetchEmptyCollection(object):
    @pytest.fixture
    def response(self, client, fantasy_database, models, db):
        db.session.query(models.Book).delete()
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

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books?include=author'


class TestSparseFieldsets(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books?fields%5Bbooks%5D=title')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_only_requested_fields(self, response):
        first_book = response.json['data'][0]
        assert list(first_book['attributes'].keys()) == ['title']
        assert 'relationships' not in first_book

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == 'http://example.com/books?fields%5Bbooks%5D=title'


class TestPagination(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books?page%5Bnumber%5D=3&page%5Bsize%5D=5')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_resource_objects_for_the_requested_page(self, response):
        assert len(response.json['data']) == 1

    def test_response_contains_self_link(self, response):
        self_link = response.json['links']['self']
        assert self_link == (
            'http://example.com/books?page%5Bnumber%5D=3&page%5Bsize%5D=5'
        )

    def test_response_contains_first_link(self, response):
        first_link = response.json['links']['first']
        assert first_link == (
            'http://example.com/books?page%5Bnumber%5D=1&page%5Bsize%5D=5'
        )

    def test_response_contains_prev_link(self, response):
        prev_link = response.json['links']['prev']
        assert prev_link == (
            'http://example.com/books?page%5Bnumber%5D=2&page%5Bsize%5D=5'
        )

    def test_response_contains_next_link(self, response):
        next_link = response.json['links']['next']
        assert next_link is None

    def test_response_contains_last_link(self, response):
        last_link = response.json['links']['last']
        assert last_link == (
            'http://example.com/books?page%5Bnumber%5D=3&page%5Bsize%5D=5'
        )


class TestResourceTypeNotFound(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/foobars')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_resource_type_not_found_error(self, response):
        assert response.json['errors'][0]['code'] == 'ResourceTypeNotFound'
