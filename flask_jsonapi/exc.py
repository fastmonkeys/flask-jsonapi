from werkzeug.exceptions import BadRequest, NotFound

from . import error_codes


class JSONAPIError(Exception):
    pass


class ResourceAlreadyRegistered(JSONAPIError):
    pass


class FieldNamingConflict(JSONAPIError):
    pass


class RequestError(JSONAPIError):
    pass


class InvalidResource(RequestError):
    def __init__(self, type):
        self.type = type


class InvalidField(RequestError):
    def __init__(self, type, field):
        self.type = type
        self.field = field

    def __str__(self):
        return '{self.type}.{self.field}'.format(self=self)


class InvalidFieldValue(RequestError):
    def __init__(self, type, value):
        self.type = type
        self.value = value


class InvalidFieldsFormat(RequestError):
    @property
    def errors(self):
        return [
            {
                "code": error_codes.INVALID_FIELDS_FORMAT,
                "status": BadRequest.code,
                "title": "Invalid fields format",
                "source": {
                    "parameter": "fields"
                }
            }
        ]


class InvalidInclude(RequestError):
    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship

    def __str__(self):
        return '{self.type}.{self.relationship}'.format(self=self)


class InvalidIncludeValue(RequestError):
    def __init__(self, value):
        self.value = value


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


class PageParametersNotAllowed(RequestError):
    def __init__(self, params):
        self.params = params


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
