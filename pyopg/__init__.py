#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""OPG Python base library.

This package supplies several python3 common library used in OPG.
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Python version requirement check
import sys
if sys.version_info < (3,6): raise ImportWarning('Python version >= 3.6 required!')
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

__all__     = []
__version__ = '.'.join(map(str, (0, 1, 0)))
__author__  = 'Lei Li <li.lei03@opg.cn>'
__date__    = '2020-11-01'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    pass
