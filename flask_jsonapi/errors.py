import json


class Error(object):
    def __init__(
        self, id=None, code=None, status=None, title=None, detail=None,
        source_path=None, source_parameter=None, meta=None
    ):
        self.id = id
        self.code = code
        self.status = status
        self.title = title
        self.detail = detail
        self.source_path = source_path
        self.source_parameter = source_parameter
        self.meta = meta

    @property
    def source_pointer(self):
        if self.source_path is not None:
            if self.source_path:
                return '/' + '/'.join(str(part) for part in self.source_path)
            return ''

    @property
    def source(self):
        source = {}
        if self.source_pointer is not None:
            source['pointer'] = self.source_pointer
        if self.source_parameter is not None:
            source['parameter'] = self.source_parameter
        return source or None

    def get_json(self):
        properties = (
            'id',
            'code',
            'status',
            'title',
            'detail',
            'source',
            'meta',
        )
        return {
            prop: getattr(self, prop)
            for prop in properties if getattr(self, prop) is not None
        }

    def __str__(self):
        return self.detail


class JSONAPIException(Exception):
    def __init__(self, *errors):
        if not errors:
            raise Exception('at least one error required')
        self.errors = errors

    @property
    def status(self):
        statuses = {error.status for error in self.errors}
        if len(statuses) > 1:
            return '400'
        else:
            return self.errors[0].status

    def get_json(self):
        return {
            'errors': [error.get_json() for error in self.errors]
        }

    def __str__(self):
        return str(self.errors[0])


class ResourceNotFound(Error):
    def __init__(self, type, id, source_path=None):
        detail = (
            'The resource identified by type "{type}" and id "{id}" could '
            'not be found'
        )
        detail = detail.format(type=type, id=id)
        Error.__init__(
            self,
            status='404',
            title='Resource Not Found',
            detail=detail,
            source_path=source_path
        )


class InvalidFieldsFormat(Error):
    def __init__(self):
        Error.__init__(
            self,
            status='400',
            title='Invalid Fields Format',
            detail='Fields parameter must specify type',
            source_parameter='fields'
        )


class InvalidResourceType(Error):
    def __init__(self, type):
        self.type = type
        Error.__init__(
            self,
            status='400',
            title='Invalid Resource Type',
            detail='"{type}" is not a valid resource type'.format(type=type),
            source_parameter='fields[{type}]'.format(type=type)
        )


class InvalidFieldsValueFormat(Error):
    def __init__(self, type):
        self.type = type
        Error.__init__(
            self,
            status='400',
            title='Invalid Fields Value Format',
            detail=(
                'The value must be a comma-separated list that refers to the '
                'name(s) of the fields to be returned'
            ),
            source_parameter='fields[{type}]'.format(type=type)
        )


class InvalidField(Error):
    def __init__(self, type, field):
        self.type = type
        self.field = field
        Error.__init__(
            self,
            status='400',
            title='Invalid Field',
            detail='"{field}" is not a valid field for "{type}"'.format(
                field=field,
                type=type
            ),
            source_parameter='fields[{type}]'.format(type=type)
        )


class InvalidInclude(Error):
    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship

        detail = '"{relationship}" is not a valid relationship of "{type}"'
        detail = detail.format(type=type, relationship=relationship)

        Error.__init__(
            self,
            status='400',
            title='Invalid Include',
            detail=detail,
            source_parameter='include'
        )


class InvalidIncludeFormat(Error):
    def __init__(self):
        Error.__init__(
            self,
            status='400',
            title='Invalid Include Format',
            detail=(
                'The value of the include parameter must be a comma-separated '
                'list of relationship paths'
            ),
            source_parameter='include'
        )


class InvalidPageFormat(Error):
    def __init__(self):
        Error.__init__(
            self,
            status='400',
            title='Invalid Page Format',
            detail='Page parameter must be an object',
            source_parameter='page'
        )


class InvalidPageParameter(Error):
    def __init__(self, param):
        detail = '"{param}" is not a valid page parameter'.format(param=param)
        Error.__init__(
            self,
            status='400',
            title='Invalid Page Parameter',
            detail=detail,
            source_parameter='page[{param}]'.format(param=param)
        )


class InvalidPageValue(Error):
    def __init__(self, param, detail=None):
        if detail is None:
            detail = 'Invalid value for "{param}" page parameter'
            detail = detail.format(param=param)
        Error.__init__(
            self,
            status='400',
            title='Invalid Page Value',
            detail=detail,
            source_parameter='page[{param}]'.format(param=param)
        )


class ParameterNotAllowed(Error):
    status = '400'
    title = 'Parameter not allowed'
    detail = '{self.source_parameter} is not a valid parameter.'

    def __init__(self, source_parameter):
        self.source_parameter = source_parameter
        Error.__init__(self)


class InvalidJSON(Error):
    status = '400'
    title = 'Request body is not valid JSON'

    def __init__(self, detail):
        self.detail = detail
        Error.__init__(self)


class ValidationError(Error):
    def __init__(self, detail, source_path):
        Error.__init__(
            self,
            status='400',
            title='Validation Error',
            detail=detail,
            source_path=source_path
        )


class TypeMismatch(Error):
    def __init__(self, actual_type, expected_type, source_path):
        detail = (
            '{actual} is not a valid type for this operation (expected '
            '{expected})'
        )
        detail = detail.format(
            actual=json.dumps(actual_type),
            expected=json.dumps(expected_type)
        )
        Error.__init__(
            self,
            status='409',
            title='Type Mismatch',
            detail=detail,
            source_path=source_path
        )


class IDMismatch(Error):
    status = '409'
    title = 'ID mismatch'
    detail = '{self.id} does not match the endpoint id.'
    source_pointer = '/data/id'

    def __init__(self, id):
        self.id = id
        Error.__init__(self)


class FullReplacementDisallowed(Error):
    def __init__(self, relationship, source_path):
        detail = 'Full replacement of {} relationship is disallowed'.format(
            json.dumps(relationship)
        )
        Error.__init__(
            self,
            status='403',
            title='Full replacement disallowed',
            detail=detail,
            source_path=source_path
        )


class ClientGeneratedIDsUnsupported(Error):
    status = '403'
    title = 'Client-generated IDs unsupported'
    detail = (
        'The server does not support creation of {self.type} resource '
        'with a client-generated ID.'
    )
    source_pointer = '/data/id'

    def __init__(self, type):
        self.type = type
        Error.__init__(self)


class ResourceAlreadyExists(Error):
    status = '409'
    title = 'Resource already exists'
    detail = (
        'A resource with ({self.type}, {self.id}) type-id pair already exists.'
    )
    source_pointer = '/data/id'

    def __init__(self, type, id):
        self.type = type
        self.id = id
        Error.__init__(self)
