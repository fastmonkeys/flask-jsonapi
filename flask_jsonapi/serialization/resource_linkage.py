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


def load(relationship, raw_data):
    func = _load_to_many if relationship.many else _load_to_one
    return func(relationship=relationship, raw_data=raw_data)


def _load_to_many(relationship, raw_data):
    parser = _parsers.Array(
        lambda item: resource_identifier.load(
            resource=relationship.resource,
            raw_data=item
        )
    )
    return parser(raw_data)


def _load_to_one(relationship, raw_data):
    if raw_data is not None:
        return resource_identifier.load(
            resource=relationship.resource,
            raw_data=raw_data
        )
