from marshmallow import post_dump, Schema, SchemaOpts

from . import fields


class JSONAPIOpts(SchemaOpts):
    def __init__(self, meta):
        SchemaOpts.__init__(self, meta)
        self.type = meta.type


class JSONAPISchema(Schema):
    OPTIONS_CLASS = JSONAPIOpts

    type = fields.Method('get_type')
    self = fields.Self()

    def get_type(self, obj):
        return self.opts.type

    @post_dump
    def add_links(self, data):
        links = {
            field_name: data.pop(field_name)
            for field_name, field in self.fields.items()
            if isinstance(field, fields.Link)
        }
        if links:
            data['links'] = links
        return data
