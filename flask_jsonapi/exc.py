class ResourceAlreadyRegistered(Exception):
    pass


class FieldNamingConflict(Exception):
    pass


class JSONAPIException(Exception):
    pass


class InvalidResource(JSONAPIException):
    def __init__(self, type):
        self.type = type


class InvalidField(JSONAPIException):
    def __init__(self, type, field):
        self.type = type
        self.field = field


class InvalidFieldValue(JSONAPIException):
    def __init__(self, type, value):
        self.type = type
        self.value = value


class InvalidFieldFormat(JSONAPIException):
    pass
