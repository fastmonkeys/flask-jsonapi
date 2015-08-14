class JSONAPIException(Exception):
    pass


class ResourceAlreadyRegistered(JSONAPIException):
    pass


class FieldNamingConflict(JSONAPIException):
    pass


class ObjectNotFound(JSONAPIException):
    pass


class ObjectAlreadyExists(JSONAPIException):
    pass


class InvalidRelationship(JSONAPIException):
    def __init__(self, model_class, relationship):
        self.model_class = model_class
        self.relationship = relationship

    def __str__(self):
        msg = '{relationship} is not a valid relationship for {model_class}.'
        return msg.format(
            relationship=self.relationship,
            model_class=self.model_class.__name__
        )
