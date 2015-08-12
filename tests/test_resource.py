import pytest

from flask_jsonapi import exceptions
from flask_jsonapi.resource import Resource
from flask_jsonapi.store.sqlalchemy import SQLAlchemyStore


@pytest.mark.parametrize('attr', ['id', 'type'])
def test_resource_cannot_have_invalid_attribute_names(db, models, attr):
    with pytest.raises(exceptions.FieldNamingConflict) as exc_info:
        Resource(
            type='books',
            model_class=models.Book,
            store=SQLAlchemyStore(db.session),
            attributes=[attr]
        )

    assert str(exc_info.value) == (
        "A resource cannot have an attribute or a relationship "
        "named 'type' or 'id'."
    )


def test_cannot_have_attribute_and_relationship_with_same_name(db, models):
    with pytest.raises(exceptions.FieldNamingConflict) as exc_info:
        Resource(
            type='books',
            model_class=models.Book,
            store=SQLAlchemyStore(db.session),
            attributes=['title'],
            relationships=['title']
        )

    assert str(exc_info.value) == (
        "A resource cannot have an attribute and a relationship "
        "with the same name."
    )
