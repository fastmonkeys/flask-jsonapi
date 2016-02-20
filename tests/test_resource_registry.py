import pytest

from flask_jsonapi import Resource, ResourceRegistry


class TestResourceRegistry(object):
    @pytest.fixture
    def registry(self):
        return ResourceRegistry()

    @pytest.fixture
    def another_registry(self):
        return ResourceRegistry()

    @pytest.fixture
    def resource(self):
        class BookResource(Resource):
            class Meta:
                type_ = 'books'

        return BookResource

    @pytest.fixture
    def another_resource(self):
        class AnotherBookResource(Resource):
            class Meta:
                type_ = 'books'

        return AnotherBookResource

    def test_is_initially_empty(self, registry):
        assert len(registry.by_type) == 0

    def test_registering_resource(self, registry, resource):
        registry.register(resource)

        assert registry.by_type['books'] is resource
        assert resource._registry is registry

    def test_cannot_register_same_type_twice(
        self,
        registry,
        resource,
        another_resource
    ):
        registry.register(resource)

        with pytest.raises(ValueError) as excinfo:
            registry.register(another_resource)

        assert str(excinfo.value) == (
            "A resource with type 'books' has already been registered."
        )

    def test_cannot_register_same_resource_twice(
        self,
        resource,
        registry,
        another_registry
    ):
        registry.register(resource)
        with pytest.raises(ValueError) as excinfo:
            another_registry.register(resource)
        assert str(excinfo.value) == (
            "{resource!r} has already been registered.".format(
                resource=resource
            )
        )
