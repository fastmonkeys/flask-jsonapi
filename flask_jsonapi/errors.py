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

    @property
    def as_json(self):
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
        return '{}: {}'.format(self.source_pointer, self.detail)


class JSONAPIException(Exception):
    def __init__(self, *errors):
        if not errors:
            raise Exception('at least one error required')
        self.errors = errors

    @property
    def status_code(self):
        status_codes = {error.status_code for error in self.errors}
        if len(status_codes) > 1:
            return '400'
        else:
            return self.errors[0].status_code

    @property
    def as_json(self):
        return {
            'errors': [error.as_json for error in self.errors]
        }

    def __str__(self):
        return str(self.errors[0])


class ResourceTypeNotFound(Error):
    status = '404'
    title = 'Resource type not found'
    detail = '{self.type} is not a valid resource type.'

    def __init__(self, type):
        self.type = type
        Error.__init__(self)


class ResourceNotFound(Error):
    def __init__(self, type, id, source_path):
        detail = (
            'The resource identified by ({type}, {id}) type-id pair could not '
            'be found.'
        ).format(
            type=json.dumps(type),
            id=json.dumps(id)
        )
        Error.__init__(
            self,
            status='404',
            title='Resource not found',
            detail=detail
        )


class RelationshipNotFound(Error):
    status = '404'
    title = 'Relationship not found'
    detail = '{self.relationship} is not a valid relationship for {self.type}.'

    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship
        Error.__init__(self)


class FieldTypeMissing(Error):
    status = '400'
    title = 'Field type missing'
    detail = 'fields must specify a type.'
    source_parameter = 'fields'


class InvalidFieldFormat(Error):
    status = '400'
    title = 'Invalid field format'
    detail = (
        'The value of fields[{self.type}] parameter must be a '
        'comma-separated list that refers to the name(s) of the fields to be '
        'returned.'
    )
    source_parameter = 'fields[{self.type}]'

    def __init__(self, type):
        self.type = type
        Error.__init__(self)


class InvalidFieldType(Error):
    status = '400'
    title = 'Invalid field'
    detail = '{self.type} is not a valid resource type.'
    source_parameter = 'fields[{self.type}]'

    def __init__(self, type):
        self.type = type
        Error.__init__(self)


class InvalidField(Error):
    status = '400'
    title = 'Invalid field'
    detail = '{self.field} is not a valid field for {self.type}.'
    source_parameter = 'fields[{self.type}]'

    def __init__(self, type, field):
        self.type = type
        self.field = field
        Error.__init__(self)


class InvalidIncludeFormat(Error):
    status = '400'
    title = 'Invalid include format'
    detail = (
        'The value of include parameter must be a comma-separated list of '
        'relationship paths.'
    )
    source_parameter = 'include'


class InvalidInclude(Error):
    status = '400'
    title = 'Invalid include'
    detail = '{self.relationship} is not a valid relationship of {self.type}.'
    source_parameter = 'include'

    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship
        Error.__init__(self)


class InvalidSortFormat(Error):
    status = '400'
    title = 'Invalid sort format'
    detail = (
        'The sort parameter must be a comma-separated list of sort fields.'
    )
    source_parameter = 'sort'


class InvalidSortField(Error):
    status = '400'
    title = 'Invalid sort field'
    detail = '{self.field} is not a sortable field for {self.type}.'
    source_parameter = 'sort'

    def __init__(self, type, field):
        self.type = type
        self.field = field
        Error.__init__(self)


class InvalidPageFormat(Error):
    status = '400'
    title = 'Invalid page format'
    source_parameter = 'page'


class InvalidPageParameter(Error):
    status = '400'
    title = 'Invalid page parameter'
    detail = '{self.param} is not a valid page parameter.'
    source_parameter = 'page[{self.param}]'

    def __init__(self, param):
        self.param = param
        Error.__init__(self)


class InvalidPageValue(Error):
    status = '400'
    title = 'Invalid page value'

    def __init__(self, detail, param):
        self.detail = detail
        self.source_parameter = 'page[{}]'.format(param)
        Error.__init__(self)


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
            title='Validation error',
            detail=detail,
            source_path=source_path
        )


class TypeMismatch(Error):
    def __init__(self, actual_type, expected_type, source_path):
        detail = (
            '{actual} is not a valid type for this operation (expected '
            '{expected})'
        ).format(
            actual=json.dumps(actual_type),
            expected=json.dumps(expected_type)
        )
        Error.__init__(
            self,
            status='409',
            title='Type mismatch',
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
    status = '403'
    title = 'Full replacement disallowed'
    detail = 'Full replacement of {self.relationship} is not allowed.'

    def __init__(self, relationship, source_pointer=None):
        self.relationship = relationship
        self.source_pointer = source_pointer
        Error.__init__(self)


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
