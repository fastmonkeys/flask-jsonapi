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

    def __str__(self):
        return '{self.type}.{self.field}'.format(self=self)


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

    def __str__(self):
        return '{self.type}.{self.relationship}'.format(self=self)


class InvalidIncludeValue(JSONAPIException):
    def __init__(self, value):
        self.value = value


class ResourceNotFound(JSONAPIException):
    def __init__(self, id):
        self.id = id


class PageParametersNotAllowed(JSONAPIException):
    def __init__(self, params):
        self.params = params


class InvalidPageValue(JSONAPIException):
    pass
