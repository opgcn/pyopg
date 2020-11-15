#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Top-level script environment for current package.

https://docs.python.org/zh-cn/3/library/__main__.html
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

from . import __version__, __author__, __date__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main

import pprint
print(f"@__package__={__package__!r} @__name__={__name__!r}")
pprint.pprint(object=globals(), indent=4)

