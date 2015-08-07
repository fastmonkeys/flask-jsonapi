from . import exc


class Parameters(object):
    def __init__(
        self, resource_registry, type, params, allow_fields=False,
        allow_include=False, allow_pagination=False
    ):
        resource = resource_registry.by_type[type]

        self.fields = FieldsParameter(
            resource_registry,
            params.pop('fields', None)
        ) if allow_fields else None

        self.include = IncludeParameter(
            resource_registry,
            type,
            params.pop('include', None)
        ) if allow_include else None

        self.pagination = resource.paginator.paginate(
            params.pop('page', {})
        ) if allow_pagination else None

        if params:
            raise exc.ParametersNotAllowed(params.keys())


class FieldsParameter(object):
    def __init__(self, resource_registry, fields):
        if fields is None:
            fields = {}
        self._resource_registry = resource_registry
        self.requested = self._parse(fields)

    def _parse(self, fields):
        try:
            field_items = fields.items()
        except AttributeError:
            raise exc.FieldTypeMissing()
        return {
            type: self._parse_requested_field_names(type, field_names)
            for type, field_names in field_items
        }

    def _parse_requested_field_names(self, type, field_names):
        resource = self._get_resource(type)
        field_names = self._split_field_names(resource, field_names)
        self._validate_field_names(resource, field_names)
        return field_names

    def _get_resource(self, type):
        try:
            return self._resource_registry.by_type[type]
        except KeyError:
            raise exc.InvalidFieldType(type)

    def _split_field_names(self, resource, field_names):
        try:
            return field_names.split(',')
        except AttributeError:
            raise exc.InvalidFieldFormat(resource.type)

    def _validate_field_names(self, resource, field_names):
        for field_name in field_names:
            if field_name not in resource.fields:
                raise exc.InvalidField(resource.type, field_name)

    def __getitem__(self, type):
        try:
            return set(self.requested[type])
        except KeyError:
            return self._resource_registry.by_type[type].fields

    def __repr__(self):
        return '<FieldsParameter {!r}>'.format(self.requested)


class IncludeParameter(object):
    def __init__(self, resource_registry, type, include):
        self._resource_registry = resource_registry
        self._type = type
        self.raw = include
        self.paths = self._parse_paths()
        self.tree = {}
        self._build_tree()

    def _build_tree(self):
        for path in self.paths:
            self._add_relationship_path_to_tree(path)

    def _parse_paths(self):
        if not self.raw:
            return []
        try:
            paths = self.raw.split(',')
        except AttributeError:
            raise exc.InvalidIncludeFormat()
        return [p.split('.') for p in paths]

    def _add_relationship_path_to_tree(self, path):
        current_node = self.tree
        resource = self._resource_registry.by_type[self._type]
        for name in path:
            if name not in current_node:
                current_node[name] = {}
            if name not in resource.relationships:
                raise exc.InvalidInclude(resource.type, name)
            related_model_class = resource.repository.get_related_model_class(
                model_class=resource.model_class,
                relationship=name
            )
            resource = self._resource_registry.by_model_class[
                related_model_class
            ]
            current_node = current_node[name]

    def __repr__(self):
        return '<IncludeParameter {raw!r}>'.format(raw=self.raw)
