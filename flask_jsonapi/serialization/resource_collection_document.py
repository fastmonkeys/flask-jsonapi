import itertools

from . import resource_identifier, resource_object


def dump(resource, obj, fields=None, include=None):
    primary_data = resource_object.dump(
        resource=resource,
        obj=obj,
        fields=params.fields
    )

    document = {'data': primary_data}

    if obj is not None:
        included = dump_included(
            resource=params.resource,
            objs=[obj],
            params=params
        )
        if included:
            document['included'] = included
    if links:
        document['links'] = links
    return document


def dump(resource, objs, params, links=None):
    primary_data = [
        resource_object.dump(
            resource=resource,
            obj=obj,
            fields=params.fields
        )
        for obj in objs
    ]
    document = {'data': primary_data}
    included = dump_included(
        resource=params.resource,
        objs=objs,
        params=params
    )
    if included:
        document['included'] = included
    if links:
        document['links'] = links
    return document


def dump_included(resource, objs, params):
    seen = {get_identifier_tuple(resource=resource, obj=obj) for obj in objs}
    included_objs = itertools.chain.from_iterable(
        iter_included_objs(
            resource=resource,
            obj=obj,
            include=params.include.tree
        )
        for obj in objs
    )
    included = []
    for resource, obj in included_objs:
        identifier = get_identifier_tuple(resource=resource, obj=obj)
        if identifier not in seen:
            resource_object = resource_object.dump(
                resource=resource,
                params=params,
                model=model
            )
            included.append(resource_object)
            seen.add(identifier)
    return included


def get_identifier_tuple(resource, obj):
    data = resource_identifier.dump(resource=resource, obj=obj)
    return data['type'], data['id']


def iter_included_objs(resource, obj, include):
    for relationship_name in include:
        relationship = resource.relationships[relationship_name]
        for related_obj in iter_related_objs(
            obj=obj,
            relationship=relationship
        ):
            yield relationship.resource, related_obj
            for included_obj in iter_included_objs(
                resource=relationship.resource,
                obj=related_obj,
                include=include[relationship_name]
            ):
                yield included_obj


def iter_related_objs(obj, relationship):
    related = getattr(obj, relationship.name)
    if relationship.many:
        for related_obj in related:
            yield related_obj
    elif related is not None:
        yield related
