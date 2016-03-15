from . import _parsers, resource_identifier


def dump(relationship, related):
    func = _dump_to_many if relationship.many else _dump_to_one
    return func(relationship=relationship, related=related)


def _dump_to_many(relationship, related):
    return [
        resource_identifier.dump(
            resource=relationship.resource,
            model=related_model
        )
        for related_model in related
    ]


def _dump_to_one(relationship, related):
    if related is not None:
        return resource_identifier.dump(
            resource=relationship.resource,
            model=related
        )


def load(relationship, data):
    func = _load_to_many if relationship.many else _load_to_one
    return func(relationship=relationship, data=data)


def _load_to_many(relationship, data):
    parser = _parsers.Array(
        lambda item: resource_identifier.load(
            resource=relationship.resource,
            data=item
        )
    )
    return parser(data)


def _load_to_one(relationship, data):
    if data is not None:
        return resource_identifier.load(
            resource=relationship.resource,
            data=data
        )
