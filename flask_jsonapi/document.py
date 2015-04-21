class Document(object):
    def __init__(self, schema, include=tuple()):
        self.schema = schema
        self.include = include

    def dump(self, objs):
        included = []
        data = []
        for obj in objs:
            data.append(self.schema.dump(obj).data)
            for relationship_path in self.include:
                related_field = self.schema.fields[relationship_path]
                related_obj = getattr(obj, relationship_path)
                related_schema = related_field.related_schema()
                if related_field.many:
                    included.extend(related_schema.dump(related_obj, many=True).data)
                else:
                    included.append(related_schema.dump(related_obj, many=False).data)
        return {
            "data": data,
            "included": included
        }
