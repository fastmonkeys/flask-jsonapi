from . import exc


class IncludeParameter(object):
    def __init__(self, resources, type, include):
        self._resources = resources
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
            raise exc.InvalidIncludeValue(self.raw)
        return [p.split('.') for p in paths]

    def _add_relationship_path_to_tree(self, path):
        current_node = self.tree
        resource = self._resources.by_type[self._type]
        for name in path:
            if name not in current_node:
                current_node[name] = {}
            if name not in resource.relationships:
                raise exc.InvalidInclude(resource.type, name)
            related_model_class = resource.repository.get_related_model_class(
                model_class=resource.model_class,
                relationship=name
            )
            resource = self._resources.by_model_class[related_model_class]
            current_node = current_node[name]

    def __repr__(self):
        return '<IncludeParameter {raw!r}>'.format(raw=self.raw)


class FieldsParameter(object):
    def __init__(self, resources, fields):
        if fields is None:
            fields = {}
        self._resources = resources
        self.requested = self._parse(fields)

    def _parse(self, fields):
        try:
            field_items = fields.items()
        except AttributeError:
            raise exc.InvalidFieldsFormat()
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
            return self._resources.by_type[type]
        except KeyError:
            raise exc.InvalidResource(type)

    def _split_field_names(self, resource, field_names):
        try:
            return field_names.split(',')
        except AttributeError:
            raise exc.InvalidFieldValue(resource.type, field_names)

    def _validate_field_names(self, resource, field_names):
        for field_name in field_names:
            if field_name not in resource.fields:
                raise exc.InvalidField(resource.type, field_name)

    def __getitem__(self, type):
        try:
            return set(self.requested[type])
        except KeyError:
            return self._resources.by_type[type].fields

    def __repr__(self):
        return '<FieldsParameter {!r}>'.format(self.requested)
