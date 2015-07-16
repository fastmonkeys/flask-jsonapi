class IncludeParameter(object):
    def __init__(self, include):
        self.raw = include
        self.tree = {}
        self._build_tree()

    @property
    def relationship_paths(self):
        if self.raw:
            for path in self.raw.split(','):
                yield RelationshipPath(path)

    def _build_tree(self):
        for path in self.relationship_paths:
            self._add_relationship_path_to_tree(path)

    def _add_relationship_path_to_tree(self, path):
        current_node = self.tree
        for name in path:
            if name not in current_node:
                current_node[name] = {}
            current_node = current_node[name]

    def __repr__(self):
        return 'IncludeParameter({raw!r})'.format(raw=self.raw)


class RelationshipPath(object):
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        return iter(self.path.split('.'))

    def __repr__(self):
        return 'RelationshipPath({path!r})'.format(path=self.path)
