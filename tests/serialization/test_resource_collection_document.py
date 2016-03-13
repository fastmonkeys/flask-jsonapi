from __future__ import unicode_literals

import pytest

from flask_jsonapi.serialization import resource_collection_document


@pytest.fixture
def books(db, models, fantasy_database):
    return db.session.query(models.Book).all()


def test_resource_collection(jsonapi, resource_registry, books, db):
    data = resource_collection_document.dump(
        resource=resource_registry.by_type['books'],
        models=books
    )
    assert len(data['data']) == 11
