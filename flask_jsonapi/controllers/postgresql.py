from .. import errors
from .default import DefaultController

try:
    from sqlalchemy_json_api import QueryBuilder
except ImportError:
    raise ImportError(
        'PostgreSQLController needs SQLAlchemy-JSON-API installed.'
    )


class PostgreSQLController(DefaultController):
    def __init__(self, resource_registry):
        self.resource_registry = resource_registry

    @property
    def query_builder(self):
        return QueryBuilder({
            type: resource.model_class
            for type, resource in self.resource_registry.by_type.items()
        })

    def _get_query(self, resource, params):
        store = resource.store
        return store._paginate(
            store.query(resource.model_class),
            params.pagination
        )

    def fetch_one(self, type, id):
        resource = self._get_resource(type)
        params = self._build_params(type)
        include = params.include.raw
        links = self._get_links(params)
        query = self.query_builder.select_one(
            resource.model_class,
            id,
            include=include.split(',') if include else None,
            fields=params.fields,
            links=links,
            from_obj=resource.store.query(resource.model_class),
            as_text=True
        )
        result = resource.store.session.execute(query).scalar()
        if result == '{"data":null}':
            raise errors.ResourceNotFound(type, id)
        return result

    def fetch(self, type):
        resource = self._get_resource(type)
        params = self._build_params(type)
        include = params.include.raw
        count = resource.store.count(resource.model_class)
        links = self._get_links(params, count)
        query = self.query_builder.select(
            resource.model_class,
            include=include.split(',') if include else None,
            fields=params.fields,
            links=links,
            from_obj=self._get_query(resource, params),
            as_text=True
        )
        return resource.store.session.execute(query).scalar()

    def fetch_related(self, type, id, relationship):
        resource = self._get_resource(type)
        relationship = self._get_relationship(resource, relationship)
        params = self._build_params(relationship.type)
        obj = self._fetch_object(resource, id)
        include = params.include.raw
        if relationship.many:
            count = resource.store.count_related(obj, relationship.name)
        else:
            count = None
        links = self._get_links(params, count)
        query = self.query_builder.select(
            relationship.model_class,
            include=include.split(',') if include else None,
            fields=params.fields,
            links=links,
            as_text=True,
            multiple=relationship.many,
            from_obj=resource.store._paginate(
                resource.store._query_related(obj, relationship.name),
                params.pagination
            )
        )
        return resource.store.session.execute(query).scalar()
