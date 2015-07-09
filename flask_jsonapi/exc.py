class ImproperlyConfigured(Exception):
    pass


class JSONAPIException(Exception):
    pass


class InvalidResource(JSONAPIException):
    pass
