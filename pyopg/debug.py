#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Utilities for debugging.

This module provides debugging utils for human beings.
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

from . import __version__, __author__, __date__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import itertools, inspect, textwrap

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def reprArgs(*t, __sep=',', **d):
    r'''Representation of arguments in an invocation, with parentheses.
    
    e.g. (val_1, val_2, key_3=val_3, key_4=val_4)
    '''
    args = __sep.join(itertools.chain( # chain generators, then join with comma
        map(repr, t),   # iterator of positional arguments
        ( f'{k}={v!r}' for k, v in d.items() ), # generator of keyword arguments
    ))
    return f"({args})"

def reprFrameLoc(index=1):
    r"""Representation of frame's module & line, from inspect.stack()[index], as arguments format.
    
    e.g. (module=module_name,line=line_number)
    https://docs.python.org/zh-cn/3/library/inspect.html#inspect.stack
    """
    frame_info = inspect.stack()[index]
    return reprArgs(module=frame_info.frame.f_globals.get('__name__'), line=frame_info.lineno)

def reprDef(obj):
    r"""Representation of a definition, without parentheses.
    
    e.g. module_name.ClassName.methodName
    - https://docs.python.org/zh-cn/3/library/stdtypes.html#definition.__qualname__
    - https://docs.python.org/zh-cn/3/reference/datamodel.html?highlight=__module__    
    """
    qualname = getattr(obj, '__qualname__', None)
    name = qualname if qualname else obj.__name__
    module = getattr(obj, '__module__', None)
    return f"{module}.{name}" if module else name

def reprCall(obj, *t, **d):
    r"""Representation of a object's invocation.
    
    e.g. module_name.func_name(args)
    """
    return reprDef(obj) + reprArgs(*t, **d)

def reprSelf(self, *t, **d):
    r"""Representation of a class instance.
    
    e.g. module_name.ClassName(args)
    """
    return reprCall(self.__class__, *t, **d)
    
def reprSelfMethod(selfMethod, *t, **d):
    r"""Representation of self.method
    
    e.g. module_name.ClassName(args).methodName(args)
    """
    return f"{repr(selfMethod.__self__)}.{selfMethod.__name__}{reprArgs(*t, **d)}"
    
def reprDesc(self, *t, **d):
    r"""Representation owner's attribute from a PEP-252 descriptor instance.
    
    e.g. <owner_module_name.OwnerClassName.attr_name>@desc_module_name.DescClassName(args)
    """
    return f"<{reprDef(self.__objclass__)}.{self.__name__}>:{reprSelf(self, *t, **d)}"
    
def reprExc(exc):
    r"""Representation of an exception instance with import attributes.
    
    e.g. repr_exception@(important_attributes_as_args_format)
    """
    repr_args = reprArgs(context=exc.__context__, suppress=exc.__suppress_context__, cause=exc.__cause__)
    return f"{exc!r}:{repr_args}"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    pass