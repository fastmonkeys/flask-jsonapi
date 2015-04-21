import json

import pytest
from flask import url_for

from ..app import app, Article, db


@pytest.fixture
def client():
    return app.test_client()


@pytest.yield_fixture(autouse=True)
def app_ctx():
    with app.app_context():
        yield


@pytest.fixture
def url():
    return url_for('jsonapi.get_many', type='articles')


@pytest.fixture
def database(request):
    db.create_all()
    request.addfinalizer(db.drop_all)


@pytest.fixture
def articles(database):
    articles = [
        Article(
            id=1,
            title="JSON API paints my bikeshed!"
        ),
        Article(
            id=2,
            title="Rails is Omakase"
        ),
    ]
    db.session.add_all(articles)
    db.session.commit()
    return articles


@pytest.fixture
def response(articles, client, url):
    return client.get(url)


def test_url(url):
    assert url == 'http://example.com/articles'


class TestSuccessfulRequest(object):
    def test_returns_200(self, response):
        assert response.status_code == 200

    def test_has_correct_content_type(self, response):
        assert response.content_type == 'application/vnd.api+json'

    def test_returns_correct_json(self, response):
        assert json.loads(response.data) == {
            "links": {
                "self": "http://example.com/articles"
            },
            "data": [
                {
                    "type": "articles",
                    "id": "1",
                    "title": "JSON API paints my bikeshed!"
                },
                {
                    "type": "articles",
                    "id": "2",
                    "title": "Rails is Omakase"
                }
            ]
        }
