from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

from . import error_codes


class Error(Exception):
    @property
    def errors(self):
        raise NotImplementedError


class InvalidJSON(Error):
    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_JSON,
                "status": BadRequest.code,
                "title": "Invalid JSON",
                "detail": "Request body is not valid JSON."
            }
        ]


class TypeMismatch(Error):
    def __init__(self, type):
        self.type = type

    @property
    def errors(self):
        return [
            {
                "code": error_codes.TYPE_MISMATCH,
                "status": Conflict.code,
                "title": "Type mismatch",
                "detail": (
                    "{type} is not a valid type for this operation."
                ).format(type=self.type),
                "source": {
                    "pointer": '/data/type'
                }
            }
        ]


class ValidationError(Error):
    def __init__(self, detail, path):
        self.detail = detail
        self.path = path

    @property
    def errors(self):
        return [
            {
                "code": error_codes.VALIDATION_ERROR,
                "status": BadRequest.code,
                "title": "Validation error",
                "detail": self.detail,
                "source": {
                    "pointer": '/' + '/'.join(self.path)
                }
            }
        ]


class InvalidResource(Error):
    def __init__(self, type_):
        self.type = type_

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_RESOURCE,
                "status": NotFound.code,
                "title": "Invalid resource",
                "detail": (
                    "{type} is not a valid resource".format(type=self.type)
                )
            }
        ]


class RelationshipNotFound(Error):
    def __init__(self, type, relation):
        self.type = type
        self.relation = relation

    @property
    def errors(self):
        return [
            {
                "code": error_codes.RELATIONSHIP_NOT_FOUND,
                "status": NotFound.code,
                "title": "Relationship not found",
                "detail": (
                    "{relation} is not a valid relationship for {type}."
                ).format(
                    relation=self.relation,
                    type=self.type
                )
            }
        ]


class ResourceNotFound(Error):
    def __init__(self, id):
        self.id = id

    @property
    def errors(self):
        return [
            {
                "code": error_codes.RESOURCE_NOT_FOUND,
                "status": NotFound.code,
                "title": "Resource not found",
                "detail": (
                    "The resource identified by {id} could not be "
                    "found.".format(id=self.id)
                )
            }
        ]


class FieldTypeMissing(Error):
    @property
    def errors(self):
        return [
            {
                "code": error_codes.FIELD_TYPE_MISSING,
                "status": BadRequest.code,
                "title": "Field type missing",
                "detail": "fields must specify a type.",
                "source": {
                    "parameter": "fields"
                }
            }
        ]


class InvalidFieldFormat(Error):
    def __init__(self, type):
        self.type = type

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_FIELD_FORMAT,
                "status": BadRequest.code,
                "title": "Invalid field format",
                "detail": (
                    "The value of fields[{type}] parameter must be a "
                    "comma-separated list that refers to the name(s) of the "
                    "fields to be returned."
                ).format(type=self.type),
                "source": {
                    "parameter": "fields[{type}]".format(type=self.type)
                }
            }
        ]


class InvalidFieldType(Error):
    def __init__(self, type):
        self.type = type

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_FIELD_TYPE,
                "status": BadRequest.code,
                "title": "Invalid field",
                "detail": "{type} is not a valid resource.".format(
                    type=self.type
                ),
                "source": {
                    "parameter": "fields[{type}]".format(type=self.type)
                }
            }
        ]


class InvalidField(Error):
    def __init__(self, type, field):
        self.type = type
        self.field = field

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_FIELD,
                "status": BadRequest.code,
                "title": "Invalid field",
                "detail": "{field} is not a valid field for {type}.".format(
                    field=self.field,
                    type=self.type
                ),
                "source": {
                    "parameter": "fields[{type}]".format(type=self.type)
                }
            }
        ]


class InvalidIncludeFormat(Error):
    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_INCLUDE_FORMAT,
                "status": BadRequest.code,
                "title": "Invalid include format",
                "detail": (
                    "The value of include parameter must be a comma-separated "
                    "list of relationship paths."
                ),
                "source": {
                    "parameter": "include"
                }
            }
        ]


class InvalidInclude(Error):
    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_INCLUDE,
                "status": BadRequest.code,
                "title": "Invalid include",
                "detail": (
                    "{relationship} is not a valid relationship of "
                    "{type}.".format(
                        relationship=self.relationship,
                        type=self.type
                    )
                ),
                "source": {
                    "parameter": "include"
                }
            }
        ]


class InvalidSortFormat(Error):
    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_SORT_FORMAT,
                "status": BadRequest.code,
                "title": "Invalid sort format",
                "detail": (
                    "The sort parameter must be a comma-separated list of "
                    "sort fields."
                ),
                "source": {
                    "parameter": "sort"
                }
            }
        ]


class InvalidSortField(Error):
    def __init__(self, type, field):
        self.type = type
        self.field = field

    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_SORT_FIELD,
                "status": BadRequest.code,
                "title": "Invalid sort field",
                "detail": "{field} is not a sortable field for {type}".format(
                    field=self.field,
                    type=self.type
                ),
                "source": {
                    "parameter": "sort"
                }
            }
        ]


class InvalidPageFormat(Error):
    @property
    def errors(self):
        return [
            {
                "status": BadRequest.code,
                "code": error_codes.INVALID_PAGE_FORMAT,
                "title": "Invalid page format",
                "source": {
                    "parameter": "page"
                }
            }
        ]


class InvalidPageParameters(Error):
    def __init__(self, params):
        self.params = params

    @property
    def errors(self):
        return [
            {
                "status": BadRequest.code,
                "code": error_codes.INVALID_PAGE_PARAMETER,
                "title": "Invalid page parameter",
                "detail": "{param} is not a valid page parameter".format(
                    param=param
                ),
                "source": {
                    "parameter": "page[{param}]".format(param=param)
                }
            } for param in sorted(self.params)
        ]


class InvalidPageValue(Error):
    def __init__(self, param, message):
        self.param = param
        self.message = message

    @property
    def errors(self):
        return [
            {
                "status": BadRequest.code,
                "code": error_codes.INVALID_PAGE_VALUE,
                "title": "Invalid page value",
                "detail": self.message,
                "source": {
                    "parameter": "page[{param}]".format(param=self.param)
                }
            }
        ]


class ParametersNotAllowed(Error):
    def __init__(self, params):
        self.params = params

    @property
    def errors(self):
        return [
            {
                "status": BadRequest.code,
                "code": error_codes.PARAMETER_NOT_ALLOWED,
                "title": "Parameter not allowed",
                "detail": "{param} is not a valid parameter".format(
                    param=param
                ),
                "source": {
                    "parameter": "{param}".format(param=param)
                }
            } for param in sorted(self.params)
        ]


class ClientGeneratedIDsUnsupported(Error):
    def __init__(self, type):
        self.type = type

    @property
    def errors(self):
        return [
            {
                "status": Forbidden.code,
                "code": error_codes.CLIENT_GENERATED_IDS_UNSUPPORTED,
                "title": "Client-generated IDs unsupported",
                "detail": (
                    "The server does not support creation of {type} resource "
                    "with a client-generated ID."
                ).format(type=self.type),
                "source": {
                    "pointer": "/data/id"
                }
            }
        ]


class ResourceAlreadyExists(Error):
    def __init__(self, type, id):
        self.type = type
        self.id = id

    @property
    def errors(self):
        return [
            {
                "status": Conflict.code,
                "code": error_codes.RESOURCE_ALREADY_EXISTS,
                "title": "Resource already exists",
                "detail": (
                    "A resource of type {type} and id {id} already exists."
                ).format(type=self.type, id=self.id),
                "source": {
                    "pointer": "/data/id"
                }
            }
        ]
