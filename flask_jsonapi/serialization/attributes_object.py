def dump(resource, model, fields=None):
    attributes = _get_included_attributes(resource=resource, fields=fields)
    raw = {attr: getattr(model, attr) for attr in attributes}
    # TODO: return resource.serialize_attributes(raw)
    return raw


def _get_included_attributes(resource, fields):
    if fields is None:
        return set(resource.attributes)
    return fields & set(resource.attributes)
