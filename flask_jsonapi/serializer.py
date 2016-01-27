import itertools

from . import link_builder


def dump_resource_object(resource, params, model):
    resource_object = dump_resource_identifier(resource=resource, model=model)

    attributes_object = dump_attributes_object(
        resource=resource,
        params=params,
        model=model
    )
    if attributes_object:
        resource_object['attributes'] = attributes_object

    relationships_object = dump_relationships_object(
        resource=resource,
        params=params,
        model=model
    )
    if relationships_object:
        resource_object['relationships'] = relationships_object

    resource_object['links'] = {
        'self': link_builder.build_individual_resource_url(
            type=resource_object['type'],
            id=resource_object['id']
        )
    }

    return resource_object


def dump_attributes_object(resource, params, model):
    return {
        attr: resource.store.get_attribute(model=model, attribute=attr)
        for attr in get_included_attributes(resource=resource, params=params)
    }


def dump_relationships_object(resource, params, model):
    return {
        relationship: dump_relationship_object(
            resource=resource,
            model=model,
            relationship_name=relationship
        )
        for relationship in get_included_relationships(
            resource=resource,
            params=params
        )
    }


def dump_relationship_object(resource, model, relationship_name):
    relationship = resource.relationships[relationship_name]
    relationship_object = {}
    if relationship.allow_include:
        relationship_object['data'] = dump_resource_linkage(
            resource=resource,
            model=model,
            relationship=relationship
        )
    relationship_object['links'] = dump_relationship_links_object(
        resource=resource,
        model=model,
        relationship=relationship
    )
    return relationship_object


def dump_relationship_links_object(resource, model, relationship):
    return {
        'self': link_builder.build_relationship_url(
            type=resource.type,
            id=resource.store.get_id(model),
            relationship=relationship.name
        ),
        'related': link_builder.build_related_url(
            type=resource.type,
            id=resource.store.get_id(model),
            relationship=relationship.name
        ),
    }


def dump_resource_linkage(resource, model, relationship):
    if relationship.many:
        func = dump_to_many_resource_linkage
    else:
        func = dump_to_one_resource_linkage
    return func(
        resource=resource,
        model=model,
        relationship=relationship
    )


def dump_to_many_resource_linkage(resource, model, relationship):
    related_models = resource.store.get_related(model, relationship.name)
    return [
        dump_resource_identifier(
            resource=relationship.resource,
            model=related_model
        )
        for related_model in related_models
    ]


def dump_to_one_resource_linkage(resource, model, relationship):
    related_model = resource.store.get_related(model, relationship.name)
    if related_model is not None:
        return dump_resource_identifier(
            resource=relationship.resource,
            model=related_model
        )


def dump_resource_identifier(resource, model):
    return {
        'type': resource.type,
        'id': resource.store.get_id(model)
    }


def get_included_attributes(resource, params):
    fields = params.fields[resource.type]
    attributes = fields & set(resource.attributes)
    return attributes


def get_included_relationships(resource, params):
    fields = params.fields[resource.type]
    relationships = fields & set(resource.relationships)
    return relationships




class Serializer(object):
    def __init__(self, resource_registry, params):
        self.resource_registry = resource_registry
        self.params = params

    def dump(self, input_, links=None):
        many = isinstance(input_, list)
        data = self._dump_primary_data(input_, many)
        included = self._dump_included_data(input_, many)
        document = {'data': data}
        if included:
            document['included'] = included
        if links:
            document['links'] = links
        return document

    def dump_relationship(self, input_, links=None):
        many = isinstance(input_, list)
        if many:
            data = [self._dump_resource_identifier(m) for m in input_]
        else:
            data = self._dump_resource_identifier(input_)
        document = {'data': data}
        if links:
            document['links'] = links
        return document

    def _dump_primary_data(self, input_, many):
        if many:
            return [self._dump_resource_object(model) for model in input_]
        elif input_ is None:
            return None
        else:
            return self._dump_resource_object(input_)


def dump_resource(resource_registry, params, model):
    resource = resource_registry.by_model_class[model.__class__]
    primary_data = dump_resource_object(
        resource=resource,
        params=params,
        model=model
    )
    document = {'data': primary_data}
    included = dump_included(
        resource_registry=resource_registry,
        models=[model],
        params=params
    )
    if included:
        document['included'] = included
    return document


def get_identifier(resource, model):
    return (resource.type, resource.store.get_id(model))


def dump_included(resource_registry, models, params):
    included_models = itertools.chain.from_iterable(
        iter_included_models(
            resource=resource_registry.by_model_class[model.__class__],
            model=model,
            include=params.include.tree
        )
        for model in models
    )
    seen = {
        get_identifier(
            resource=resource_registry.by_model_class[model.__class__],
            model=model
        )
        for model in models
    }
    included = []
    for model in included_models:
        resource = resource_registry.by_model_class[model.__class__]
        identifier = get_identifier(resource=resource, model=model)
        if identifier not in seen:
            resource_object = dump_resource_object(
                resource=resource,
                params=params,
                model=model
            )
            included.append(resource_object)
            seen.add(identifier)
    return included


def iter_included_models(resource, model, include):
    for relationship_name in include:
        relationship = resource.relationships[relationship_name]
        for related_model in iter_related_models(
            resource=resource,
            model=model,
            relationship=relationship
        ):
            yield related_model
            for m in iter_included_models(
                resource=relationship.resource,
                model=related_model,
                include=include[relationship_name]
            ):
                yield m


def iter_related_models(resource, model, relationship):
    related = resource.store.get_related(model, relationship.name)
    if relationship.many:
        for related_model in related:
            yield related_model
    elif related is not None:
        yield related
