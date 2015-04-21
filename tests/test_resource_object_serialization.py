import pytest

from flask_jsonapi import fields, JSONAPISchema

from .app import app, Article, Comment, Person


@pytest.yield_fixture(autouse=True)
def app_ctx():
    with app.app_context():
        yield


class TestResourceObjectSerializationWithoutRelations(object):
    @pytest.fixture
    def schema(self):
        class ArticleSchema(JSONAPISchema):
            id = fields.String()
            title = fields.String()

            class Meta:
                type = 'articles'

        return ArticleSchema()

    @pytest.fixture
    def article(self):
        return Article(
            id=1,
            title='Rails is Omakase'
        )

    def test_serialized_resource(self, article, schema):
        result = schema.dump(article)
        assert result.data == {
            "type": "articles",
            "id": "1",
            "title": "Rails is Omakase",
            "links": {
                "self": "http://example.com/articles/1"
            }
        }


class TestResourceObjectSerializationWithRelationsAsURLs(object):
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
            comments = fields.Related(CommentSchema, many=True, as_object=False)
            author = fields.Related(PersonSchema, as_object=False)

            class Meta:
                type = 'articles'

        return ArticleSchema()

    @pytest.fixture
    def person(self):
        return Person(id=9)

    @pytest.fixture
    def article(self, person):
        return Article(
            id=1,
            title='Rails is Omakase',
            author=person
        )

    def test_serialize_resource(self, article, schema):
        result = schema.dump(article)
        assert result.data == {
            "type": "articles",
            "id": "1",
            "title": "Rails is Omakase",
            "links": {
                "self": "http://example.com/articles/1",
                "author": "http://example.com/articles/1/author",
                "comments": "http://example.com/articles/1/comments"
            }
        }


class TestResourceObjectSerializationWithEmptyRelationsAsObjects(object):
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

    @pytest.fixture
    def article(self):
        return Article(
            id=1,
            title='Rails is Omakase',
            author=None
        )

    def test_serialize_resource(self, article, schema):
        result = schema.dump(article)
        assert result.data == {
            "type": "articles",
            "id": "1",
            "title": "Rails is Omakase",
            "links": {
                "self": "http://example.com/articles/1",
                "author": {
                    "self": "http://example.com/articles/1/links/author",
                    "related": "http://example.com/articles/1/author",
                    "linkage": None
                },
                "comments": {
                    "self": "http://example.com/articles/1/links/comments",
                    "related": "http://example.com/articles/1/comments",
                    "linkage": []
                },
            }
        }


class TestResourceObjectSerializationWithNonEmptyRelationsAsObjects(object):
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

    @pytest.fixture
    def article(self):
        return Article(
            id=1,
            title='Rails is Omakase',
            author=Person(id=9),
            comments=[
                Comment(id=5),
                Comment(id=12),
            ]
        )

    def test_serialize_resource(self, article, schema):
        result = schema.dump(article)
        assert result.data == {
            "type": "articles",
            "id": "1",
            "title": "Rails is Omakase",
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
                        },
                    ]
                },
            }
        }
