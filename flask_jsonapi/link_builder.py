from flask import url_for


class LinkBuilder(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def resource_self_link(self, resource, obj):
        data = resource_identifier.dump(resource=resource, obj=obj)
        return '{base_url}/{type}/{id}'.format(base_url=self.base_url, **data)

    def relationship_self_link(self, relationship, obj):
        return '{resource_self_link}/relationships/{relationship}'.format(
            resource_self_link=self.resource_self_link(
                resource=relationship.parent,
                obj=obj
            )
        )

    def relationship_related_link(self, relationship, obj):
        return '{resource_self_link}/{relationship}'.format(
            resource_self_link=self.resource_self_link(
                resource=relationship.parent,
                obj=obj
            )
        )
