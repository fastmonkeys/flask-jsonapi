import qstring

from . import exc


# criteria
#  - sort
#  - include
#  - fields
#  - filter
#  - page

class Parameters(object):
    def __init__(self, request):
        params = request.args
        self.include = IncludeParameter(request)
        self.fields = FieldsParameter()


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
            raise exc.InvalidFieldFormat()
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
