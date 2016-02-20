from . import resource_identifier


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
