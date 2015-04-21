import pytest

from flask_jsonapi import Document, fields, JSONAPISchema
from tests.app import app, Article, Comment, Person


@pytest.yield_fixture(autouse=True)
def app_ctx():
    with app.app_context():
        yield


class TestCompoundDocument(object):
    @pytest.fixture
    def articles(self):
        return [
            Article(
                id=1,
                title='JSON API paints my bikeshed!',
                author=Person(
                    id=9,
                    first_name='Dan',
                    last_name='Gebhardt',
                    twitter='dgeb'
                ),
                comments=[
                    Comment(id=5, body='First!'),
                    Comment(id=12, body='I like XML better')
                ]
            )
        ]

    @pytest.fixture
    def schema(self):
        class PersonSchema(JSONAPISchema):
            id = fields.String()
            first_name = fields.String()
            last_name = fields.String()
            twitter = fields.String()

            class Meta:
                type = 'people'

        class CommentSchema(JSONAPISchema):
            id = fields.String()
            body = fields.String()

            class Meta:
                type = 'comments'

        class ArticleSchema(JSONAPISchema):
            id = fields.String()
            title = fields.String()
            comments = fields.Related(CommentSchema, many=True, as_object=True)
            author = fields.Related(PersonSchema, as_object=True)

            class Meta:
                type = 'articles'

        return ArticleSchema()

    def test_serialized(self, articles, schema):
        document = Document(schema, include=('author', 'comments'))
        serialized_document = document.dump(articles)

        assert serialized_document['data'] == [
            {
                "type": "articles",
                "id": "1",
                "title": "JSON API paints my bikeshed!",
                "links": {
                    "self": "http://example.com/articles/1",
                    "author": {
                        "self": "http://example.com/articles/1/links/author",
                        "related": "http://example.com/articles/1/author",
                        "linkage": {
                            "type": "people",
                            "id": "9"
                        }
                    },
                    "comments": {
                        "self": "http://example.com/articles/1/links/comments",
                        "related": "http://example.com/articles/1/comments",
                        "linkage": [
                            {
                                "type": "comments",
                                "id": "5"
                            },
                            {
                                "type": "comments",
                                "id": "12"
                            }
                        ]
                    }
                }
            }
        ]
        assert serialized_document['included'] == [
            {
                "type": "people",
                "id": "9",
                "first_name": "Dan",
                "last_name": "Gebhardt",
                "twitter": "dgeb",
                "links": {
                    "self": "http://example.com/people/9"
                }
            },
            {
                "type": "comments",
                "id": "5",
                "body": "First!",
                "links": {
                    "self": "http://example.com/comments/5"
                }
            },
            {
                "type": "comments",
                "id": "12",
                "body": "I like XML better",
                "links": {
                    "self": "http://example.com/comments/12"
                }
            }
        ]
