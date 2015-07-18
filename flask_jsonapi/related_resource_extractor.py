def iter_included_models(resources, model, include):
    resource = resources._by_model_class[model.__class__]
    repository = resource.repository
    for relationship in include:
        if repository.is_to_many_relationship(model, relationship):
            related_models = repository.get_related(model, relationship)
            for related_model in related_models:
                yield related_model
                for m in iter_included_models(
                    resources,
                    related_model,
                    include[relationship]
                ):
                    yield m
        else:
            related_model = repository.get_related(model, relationship)
            if related_model is not None:
                yield related_model
                for m in iter_included_models(
                    resources,
                    related_model,
                    include[relationship]
                ):
                    yield m
