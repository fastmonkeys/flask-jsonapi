# -*- coding: utf-8 -*-
import sys

is_py3 = sys.version_info[0] > 2

if is_py3:  # pragma: no cover
    string_types = str
else:       # pragma: no cover
    string_types = basestring
