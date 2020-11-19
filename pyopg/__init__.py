#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""OPG Python base library.

See https://github.com/opgcn/pyopg
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# package metadata

__all__     = []
__version__ = '.'.join(map(str, (0, 1, 0)))
__author__  = 'Li Lei'
__date__    = '2020-11-01'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# package initialization

# Check Python version requirement.
_pkg_py_ver = (3, 6)
import sys
if sys.version_info < _pkg_py_ver:
    raise RuntimeError('Python version >= %s required for package %r!' % ('.'.join(map(str, _pkg_py_ver)), __package__))

# Print package level debug info.
_pkg_print_debug = False
if _pkg_print_debug:
    import pprint
    print(f"@__package__={__package__!r} @__name__={__name__!r}")
    pprint.pprint(object=globals(), depth=1, indent=4)
