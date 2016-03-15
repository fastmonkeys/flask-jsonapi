class JSONAPIException(Exception):
    pass


class ResourceAlreadyRegistered(JSONAPIException):
    pass


class ObjectNotFound(JSONAPIException):
    pass


class ObjectAlreadyExists(JSONAPIException):
    pass
