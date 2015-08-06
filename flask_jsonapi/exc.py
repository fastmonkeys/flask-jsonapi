from werkzeug.exceptions import BadRequest, NotFound

from . import error_codes


class JSONAPIError(Exception):
    pass


class ResourceAlreadyRegistered(JSONAPIError):
    pass


class FieldNamingConflict(JSONAPIError):
    pass


class RequestError(JSONAPIError):
    @property
    def errors(self):
        raise NotImplementedError


class InvalidResource(RequestError):
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


class ResourceNotFound(RequestError):
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


class FieldTypeMissing(RequestError):
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


class InvalidFieldFormat(RequestError):
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


class InvalidFieldType(RequestError):
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


class InvalidField(RequestError):
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


class InvalidIncludeFormat(RequestError):
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


class InvalidInclude(RequestError):
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


class InvalidSortFormat(RequestError):
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


class InvalidSortField(RequestError):
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


class InvalidPageFormat(RequestError):
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


class InvalidPageParameters(RequestError):
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


class InvalidPageValue(RequestError):
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
