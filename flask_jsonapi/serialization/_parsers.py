import json

from .._compat import string_types
from ..errors import JSONAPIException, ValidationError


class Object(object):
    def __init__(
        self, properties=None, required=None, additional_properties=True
    ):
        self.properties = properties or {}
        self.required = required or []
        self.additional_properties = additional_properties

    def __call__(self, raw_data):
        self._raw_data = raw_data
        self._errors = []
        self._data = {}

        self._check_type()
        self._check_properties()
        self._check_required_properties()
        self._check_additional_properties()

        if self._errors:
            raise JSONAPIException(*self._errors)

        return self._data

    def _check_type(self):
        _check_type(
            python_type=dict,
            json_type='object',
            raw_data=self._raw_data
        )

    def _check_properties(self):
        for property_name, raw_value in sorted(self._raw_data.items()):
            parser = self.properties.get(property_name, Any())
            try:
                self._data[property_name] = parser(raw_value)
            except JSONAPIException as exc:
                for error in exc.errors:
                    if error.source_path is not None:
                        error.source_path.insert(0, property_name)
                    self._errors.append(error)

    def _check_required_properties(self):
        for property_name in self.required:
            if property_name not in self._raw_data:
                detail = '"{}" is a required property'.format(property_name)
                error = ValidationError(detail=detail, source_path=[])
                self._errors.append(error)

    def _check_additional_properties(self):
        extra = set(self._raw_data.keys()) - set(self.properties)
        if not self.additional_properties and extra:
            detail = (
                'Additional properties are not allowed ({extra} {verb} '
                'unexpected)'
            ).format(
                extra=', '.join(
                    json.dumps(property_name)
                    for property_name in sorted(extra)
                ),
                verb='was' if len(extra) == 1 else 'were'
            )
            error = ValidationError(detail=detail, source_path=[])
            self._errors.append(error)


class Array(object):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, raw_data):
        self._raw_data = raw_data
        self._errors = []
        self._data = []

        self._check_type()
        self._check_items()

        if self._errors:
            raise JSONAPIException(*self._errors)

        return self._data

    def _check_type(self):
        _check_type(
            python_type=list,
            json_type='array',
            raw_data=self._raw_data
        )

    def _check_items(self):
        for index, raw_item in enumerate(self._raw_data):
            try:
                item = self.parser(raw_item)
            except JSONAPIException as exc:
                for error in exc.errors:
                    if error.source_path is not None:
                        error.source_path.insert(0, index)
                    self._errors.append(error)
            else:
                self._data.append(item)


class Any(object):
    def __call__(self, raw_data):
        return raw_data


class String(object):
    def __call__(self, raw_data):
        self._check_type(raw_data)
        return raw_data

    def _check_type(self, raw_data):
        _check_type(
            python_type=string_types,
            json_type='string',
            raw_data=raw_data
        )


def _check_type(python_type, json_type, raw_data):
    if not isinstance(raw_data, python_type):
        detail = "{json} is not of type '{json_type}'".format(
            json=json.dumps(raw_data),
            json_type=json_type
        )
        error = ValidationError(detail=detail, source_path=[])
        raise JSONAPIException(error)
