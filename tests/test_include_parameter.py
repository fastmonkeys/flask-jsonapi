import pytest

from flask_jsonapi.include_parameter import IncludeParameter, RelationshipPath


class TestIncludeParameter(object):
    @pytest.mark.parametrize(
        ('include', 'tree'),
        [
            ('', {}),
            ('comments', {'comments': {}}),
            ('comments.author', {'comments': {'author': {}}}),
            ('comments.author,comments', {'comments': {'author': {}}}),
        ]
    )
    def test_tree(self, include, tree):
        assert IncludeParameter(include).tree == tree

    def test___repr__(self):
        include = IncludeParameter('comments.author,comments')
        assert repr(include) == "IncludeParameter('comments.author,comments')"


class TestRelationshipPath(object):
    @pytest.fixture
    def path(self):
        return RelationshipPath('comments.author')

    def test___iter__(self, path):
        names = iter(path)
        assert next(names) == 'comments'
        assert next(names) == 'author'
        with pytest.raises(StopIteration):
            next(names)

    def test___repr__(self, path):
        assert repr(path) == "RelationshipPath('comments.author')"
