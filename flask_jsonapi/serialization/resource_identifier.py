def dump(resource, model):
    return {
        'type': resource.type,
        'id': str(getattr(model, 'id'))
    }
