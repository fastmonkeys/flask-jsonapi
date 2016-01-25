# -*- coding: utf-8 -*-
import sys

is_py2 = sys.version_info[0] == 2

if is_py2:  # pragma: no cover
    string_types = basestring
else:       # pragma: no cover
    string_types = str
