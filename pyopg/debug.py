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
import inspect, logging, contextlib, functools, itertools

from . import color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Representation

def reprArgs(*t, __sep=', ', **d):
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
    
def reprDesc(self, *t, **d):
    r"""Representation owner's attribute from a PEP-252 descriptor instance.
    
    e.g. <owner_module_name.OwnerClassName.attr_name>@desc_module_name.DescClassName(args)
    """
    return f"<{reprDef(self.__objclass__)}.{self.__name__} = {reprSelf(self, *t, **d)}>"
    
def reprExc(exc):
    r"""Representation of an exception instance with import attributes.
    
    e.g. repr_exception@(important_attributes_as_args_format)
    """
    repr_args = reprArgs(context=exc.__context__, suppress=exc.__suppress_context__, cause=exc.__cause__)
    return f"<{exc!r}:{repr_args}>"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Logging

# OPG default log format pattern
LOG_FMT_DFT = "[{asctime}][{module}:{funcName}:{lineno}][{levelname}][{name}] {message}"

LOG_HANDLER_COLOR = logging.StreamHandler()
LOG_HANDLER_COLOR.setFormatter(logging.Formatter(style='{', fmt=LOG_FMT_DFT.format(
    asctime     = color.Seq(color.STY.UNDER,  color.BG.B_BLACK, color.FG.WHITE)('{asctime}'),
    module      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{module}'),
    funcName    = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{funcName}'),
    lineno      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{lineno}'),
    levelname   = color.Seq(color.STY.BLINK,  color.BG.B_BLACK, color.FG.RED  )('{levelname}'),
    name        = color.Seq(color.STY.ITALIC, color.BG.B_BLACK, color.FG.CYAN )('{name}'),
    message     = '{message}',
)))

def loggedFunc(logger=None, level=logging.DEBUG):
    r'''A decorator wraps longging on function call's begin and end with given logger and level.
    
    Deprecated: use 'Logged' instead.
    '''
    # loggedFunc(logger)(func)(*t, **d) -> _inner_decorator(func)(*t, **d) -> _wrapper(*t, **d)
    def _inner_decorator(func): # pure decorator
        if not logger: # logger not given
            return func # no wraps needed
        @functools.wraps(func)
        def _wrapper(*t, **d):
            repr_call = reprCall(func, *t, **d)
            logger.log(level, f'{repr_call} starting')
            try:
                result = func(*t, **d) # original func() is 'wrapped function'
            except Exception as exc: # intercept any exception for logging
                logger.log(level, f'{repr_call} raised: {reprExc(exc)}')
                raise # reraise exception of original wrapped out this wrapper
            else: # no exception then log what returned
                logger.log(level, f'{repr_call} returned: {result!r}')
                return result # from _wrapper()
        return _wrapper # from _inner_decorator()
    return _inner_decorator # from loggedFunc()

@contextlib.contextmanager
def loggedContext(logger=None, level=logging.DEBUG, *t, **d):
    r'''A context manager supports longging on code block begin and end with given logger, level.
    
    Deprecated: use 'Logged' instead.
    '''
    _repr_loc = reprFrameLoc(index=3)
    _repr = f"<with@{_repr_loc}>"
    if logger:
        logger.log(level, f'{_repr} entered')
    try:
        yield _repr
    except Exception as exc:
        if logger:
            logger.log(level, f'{_repr} raised: {reprExc(exc)}')
        raise # otherwise the contextlib.contextmanager will indicate to exception has been handled
    else:
        if logger:
            logger.log(level, f'{_repr} exited')

class Logged(contextlib.ContextDecorator):
    r"""A context manager and decorator to log starting and finishing.
    """
    def __init__(self, logger=None, level=logging.DEBUG, *t, **d):
        r"""Initialization.
        """
        self._logger, self._level = logger, level
        self._t, self._d = t, d

    def __repr__(self):
        r"""Representation.
        """
        repr_loc = reprFrameLoc(index=2)
        return f"<{reprSelf(self, *self._t, **self._d)}@{repr_loc}>"

    def __enter__(self):
        r"""Enter method returns self for representation in with clause.
        """
        if self._logger:
            self._logger.log(self._level, f'{self} entering')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        r"""Exit method retains its optional exception handling even when used as a decorator.
        """
        if self._logger:
            if exc_val:
                self._logger.log(self._level, f'{self} raised: {reprExc(exc_val)}')
            else:
                self._logger.log(self._level, f'{self} exited')
        return False

    def __call__(self, func):
        r"""As a decorator.
        """
        if not self._logger: # logger not given
            return func # no wraps needed
        @functools.wraps(func)
        def _wrapper(*t, **d):
            repr_call = reprCall(func, *t, **d)
            self._logger.log(self._level, f'{repr_call} starting')
            try:
                result = func(*t, **d) # original func() is 'wrapped function'
            except Exception as exc: # intercept any exception for logging
                self._logger.log(self._level, f'{repr_call} raised: {reprExc(exc)}')
                raise # reraise exception of original wrapped out this wrapper
            else: # no exception then log what returned
                self._logger.log(self._level, f'{repr_call} returned: {result!r}')
                return result # from _wrapper()
        return _wrapper # from _inner_decorator()
        
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(LOG_HANDLER_COLOR) # as app
    logger.setLevel(logging.DEBUG)

    logger.info('now demonstrates decorator')
    try:
        @Logged(logger=logger)
        def f(a=1, b=2, *t, **d):
            r"""This is some function.
            """
            logger.info(f'now works in some function')
            raise RuntimeWarning('exc raised in a function')
            return a+b
        logger.info(f"__name__ of f()'s wrapper is {f.__name__!r}")
        f(10, 20, 30, z=100)
    except Exception as exc:
        logger.warning(f'caught exception: {reprExc(exc)}')
        
    logger.info('now demonstrates context manager')
    def f():
        try:
            with Logged(logger=logger, note="My-Processing") as ctx:
                logger.info(f'now works in {ctx}')
                raise RuntimeWarning('code block raised this exception')
                print("this satement will never run!")
        except Exception as exc:
            logger.warning(f'caught exception: {reprExc(exc)}')
    f()