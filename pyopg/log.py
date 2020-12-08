#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Utilities for logging.

This module provides logging utils for human beings.
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

from . import __version__, __author__, __date__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import functools, itertools, contextlib, logging

from . import debug, color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# OPG default log format pattern
fmt_default = "[{asctime}][{module}:{funcName}:{lineno}][{levelname}][{name}] {message}"

handler_color = logging.StreamHandler()
handler_color.setFormatter(logging.Formatter(style='{', fmt=fmt_default.format(
    asctime     = color.Seq(color.STY.UNDER,  color.BG.B_BLACK, color.FG.WHITE)('{asctime}'),
    module      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{module}'),
    funcName    = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{funcName}'),
    lineno      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK, color.FG.GREEN)('{lineno}'),
    levelname   = color.Seq(color.STY.BLINK,  color.BG.B_BLACK, color.FG.RED  )('{levelname}'),
    name        = color.Seq(color.STY.ITALIC, color.BG.B_BLACK, color.FG.CYAN )('{name}'),
    message     = '{message}',
)))

def decorator(logger=None, level=logging.DEBUG):
    r'''A decorator wraps longging on function call's begin and end with given logger and level.
    '''
    # decorator(logger)(func)(*t, **d) -> _inner_decorator(func)(*t, **d) -> _wrapper(*t, **d)
    def _inner_decorator(func): # pure decorator
        if not logger: # logger not given
            return func # no wraps needed
        @functools.wraps(func)
        def _wrapper(*t, **d):
            repr_call = debug.reprCall(func, *t, **d)
            logger.log(level, f'{repr_call} starting')
            try:
                result = func(*t, **d) # original func() is 'wrapped function'
            except Exception as exc: # intercept any exception for logging
                logger.log(level, f'{repr_call} raised: {debug.reprExc(exc)}')
                raise # reraise exception of original wrapped out this wrapper
            else: # no exception then log what returned
                logger.log(level, f'{repr_call} returned: {result!r}')
                return result # from _wrapper()
        return _wrapper # from _inner_decorator()    
    return _inner_decorator # from decorator()

class Context(contextlib.ContextDecorator):
    r"""A context manager to log starting and finishing.
    """
    def __init__(self, logger=None, level=logging.DEBUG, *t, **d):
        r"""Initialization.
        """
        self._logger, self._level = logger, level
        super().__init__(*t, **d)

    def __repr__(self):
        r"""Representation.
        """
        repr_loc = debug.reprFrameLoc(index=2)
        return f"{debug.reprSelf(self)}@{repr_loc}" 

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
                self._logger.log(self._level, f'{self} raised: {debug.reprExc(exc_val)}')
            else:
                self._logger.log(self._level, f'{self} exited')
        return False

@contextlib.contextmanager
def context(logger=None, level=logging.DEBUG):
    r'''A context manager supports longging on code block begin and end with given logger, level.
    
    Deprecated: use `Context` class instead.
    '''
    _repr_loc = debug.reprFrameLoc(index=3)
    _repr = f"with@{_repr_loc}"
    if logger:
        logger.log(level, f'{_repr} entered')
    try:
        yield _repr
    except Exception as exc:
        if logger:
            logger.log(level, f'{_repr} raised: {debug.reprExc(exc)}')
        raise # otherwise the contextlib.contextmanager will indicate to exception has been handled
    else:
        if logger:
            logger.log(level, f'{_repr} exited')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(handler_color) # as app
    logger.setLevel(logging.DEBUG)

    logger.info('now demonstrates decorator')
    try:
        @decorator(logger=logger)
        def f(a=1, b=2, *t, **d):
            r"""This is some function.
            """
            logger.info(f'now works in some function')
            raise RuntimeWarning('exc raised in a function')
            return a+b
        logger.info(f"__name__ of f()'s wrapper is {f.__name__!r}")
        f(10, 20, 30, z=100)
    except Exception as exc:
        logger.warning(f'caught exception: {debug.reprExc(exc)}')
        
    logger.info('now demonstrates context manager')
    def f():
        try:
            with Context(logger=logger) as ctx:
                logger.info(f'now works in {ctx}')
                raise RuntimeWarning('code block raised this exception')
                print("this satement will never run!")
        except Exception as exc:
            logger.warning(f'caught exception: {debug.reprExc(exc)}')
    f()
