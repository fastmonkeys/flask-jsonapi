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


class InvalidInclude(JSONAPIException):
    def __init__(self, type, relationship):
        self.type = type
        self.relationship = relationship


class InvalidIncludeValue(JSONAPIException):
    def __init__(self, value):
        self.value = value
