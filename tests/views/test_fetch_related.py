import pytest


@pytest.fixture(params=[
    'flask_jsonapi.controllers.default.DefaultController',
    'flask_jsonapi.controllers.postgresql.PostgreSQLController',
])
def controller_class(request):
    return request.param


class TestSuccessfulRequestToOneRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/author')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_the_requested_resource(self, response):
        data = response.json['data']
        assert data['type'] == 'authors'
        assert data['id'] == '1'


class TestSuccessfulRequestEmptyToOneRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/11/series')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_the_requested_resource(self, response):
        assert response.json['data'] is None


class TestSuccessfulRequestToManyRelation(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/1/chapters')

    def test_responds_with_200_status_code(self, app, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['data']) == 20


class TestSuccessfulRequestEmptyToManyRelation(object):
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


class TestToManyRelationWithIncludedRelatedResources(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/2/books?include=author')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_requested_related_resources(self, response):
        assert len(response.json['included']) == 2


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


class TestToManyRelationPagination(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/stores/2/books?page%5Bnumber%5D=3&page%5Bsize%5D=5')

    def test_responds_with_200_status_code(self, response):
        assert response.status_code == 200

    def test_returns_resource_objects_for_the_requested_page(self, response):
        assert len(response.json['data']) == 2


class TestRequestInvalidResource(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/foo/1/bar')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'INVALID_RESOURCE'


class TestResourceNotFound(object):
    @pytest.fixture
    def response(self, client, fantasy_database):
        return client.get('/books/123123/chapters')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'RESOURCE_NOT_FOUND'


class TestInvalidRelationship(object):
    @pytest.fixture
    def response(self, client):
        return client.get('/books/1/foobar')

    def test_responds_with_404_status_code(self, response):
        assert response.status_code == 404

    def test_returns_invalid_resource_error(self, response):
        assert response.json['errors'][0]['code'] == 'RELATIONSHIP_NOT_FOUND'
