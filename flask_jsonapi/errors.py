class Error(Exception):
    id = None
    status = None
    title = None
    detail = None
    source_pointer = None
    source_parameter = None
    meta = None

    def __init__(self):
        if self.detail:
            self.detail = self.detail.format(self=self)
        if self.source_parameter:
            self.source_parameter = self.source_parameter.format(self=self)

    @property
    def code(self):
        return self.__class__.__name__

    @property
    def source(self):
        source = {}
        if self.source_pointer is not None:
            source['pointer'] = self.source_pointer
        if self.source_parameter is not None:
            source['parameter'] = self.source_parameter
        return source or None

    @property
    def as_dict(self):
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


class ResourceTypeNotFound(Error):
    status = '404'
    title = 'Resource type not found'
    detail = '{self.type} is not a valid resource type.'

    def __init__(self, type):
        self.type = type
        Error.__init__(self)


class ResourceNotFound(Error):
    status = '404'
    title = 'Resource not found'
    detail = (
        'The resource identified by ({self.type}, {self.id}) type-id pair '
        'could not be found.'
    )

    def __init__(self, type, id, source_pointer=None):
        self.type = type
        self.id = id
        self.source_pointer = source_pointer
        Error.__init__(self)


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
    status = '400'
    title = 'Validation error'

    def __init__(self, detail, source_pointer):
        self.detail = detail
        self.source_pointer = source_pointer
        Error.__init__(self)


class TypeMismatch(Error):
    status = '409'
    title = 'Type mismatch'
    detail = '{self.type} is not a valid type for this operation.'

    def __init__(self, type, source_pointer=None):
        self.type = type
        self.source_pointer = source_pointer
        Error.__init__(self)


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
