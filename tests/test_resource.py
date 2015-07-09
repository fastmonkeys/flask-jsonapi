import pytest

from jsonapi import exc
from jsonapi.resource import Resource


def test_resource_must_have_type():
    with pytest.raises(exc.ImproperlyConfigured) as exc_info:
        class ArticleResource(Resource):
            pass

    assert str(exc_info.value) == (
        'ArticleResource.Meta.type must be specified.'
    )


def test_resource_must_have_model_cls():
    with pytest.raises(exc.ImproperlyConfigured) as exc_info:
        class ArticleResource(Resource):
            class Meta:
                type = 'articles'

    assert str(exc_info.value) == (
        'ArticleResource.Meta.model_class must be specified.'
    )


def test_resource_model_cls_must_be_sqlalchemy_model():
    class Article(object):
        pass

    with pytest.raises(exc.ImproperlyConfigured) as exc_info:
        class ArticleResource(Resource):
            class Meta:
                type = 'articles'
                model_class = Article

    assert str(exc_info.value) == (
        'ArticleResource.Meta.model_class must be a class mapped by '
        'SQLAlchemy.'
    )


@pytest.mark.parametrize('attr', ['id', 'type'])
def test_resource_cannot_have_invalid_attribute_names(models, attr):
    with pytest.raises(exc.ImproperlyConfigured) as exc_info:
        class BookResource(Resource):
            class Meta:
                type = 'books'
                model_class = models.Book
                attributes = [attr]

    assert str(exc_info.value) == (
        "BookResource: a resource cannot have an attribute or a relationship "
        "named 'type' or 'id'."
    )


def test_cannot_have_attribute_and_relationship_with_same_name(models):
    with pytest.raises(exc.ImproperlyConfigured) as exc_info:
        class BookResource(Resource):
            class Meta:
                type = 'books'
                model_class = models.Book
                attributes = ['title']
                relationships = ['title']

    assert str(exc_info.value) == (
        "BookResource: a resource cannot have an attribute and a relationship "
        "with the same name ('title')."
    )
