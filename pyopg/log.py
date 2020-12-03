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
import functools, itertools, contextlib, inspect, logging, weakref

# import compatibale functools.cached_property() new in python 3.8
if not hasattr(functools, 'cached_property'):
    from . import new3
    functools.cached_property = new3.cached_property

from . import color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# OPG default log format pattern
fmt_default = "[{asctime}][{module}:{funcName}:{lineno}][{levelname}][{name}] {message}"

handler_color = logging.StreamHandler()
handler_color.setFormatter(logging.Formatter(style='{', fmt=fmt_default.format(
    asctime     = color.Seq(color.STY.RESET,  color.BG.B_BLACK,   color.FG.WHITE  )('{asctime}'),
    module      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK,   color.FG.GREEN  )('{module}'),
    funcName    = color.Seq(color.STY.BOLD,   color.BG.B_BLACK,   color.FG.GREEN  )('{funcName}'),
    lineno      = color.Seq(color.STY.BOLD,   color.BG.B_BLACK,   color.FG.GREEN  )('{lineno}'),
    levelname   = color.Seq(color.STY.BOLD,   color.BG.B_BLACK,   color.FG.YELLOW )('{levelname}'),
    name        = color.Seq(color.STY.BOLD,   color.BG.B_BLACK,   color.FG.CYAN   )('{name}'),
    message     = '{message}',
)))

def reprArgs(*t, **d):
    r'''Return arguments' representation string as in function invocation.
    '''
    return ', '.join(itertools.chain( # chain generators, then join with comma
        (repr(arg) for arg in t),   # generator of positional arguments
        (f'{k}={v!r}' for (k, v) in d.items()), # generator of keyword arguments
    ))

def reprExc(exc):
    r"""Return a detailed representation string of an exception instance.
    """
    return f"repr={exc!r} context={exc.__context__!r} suppress_context={exc.__suppress_context__!r} cause={exc.__cause__!r}"

class ContextDecorator(contextlib.ContextDecorator):
    r"""A logging context manager also can be used as a decorator.
    """
    def __init__(self, logger, level=logging.DEBUG, *t, **d):
        r"""Initialization.
        """
        self.__logger = logger
        self.__level = level
        self.__at = None
        super().__init__(*t, **d)

    def __str__(self):
        r"""Logging location string as <module>:<lineno> for context manager, and as <func>(<args>) for decorator.
        """
        return self.__at
        
    def __call__(self, func):
        r"""Syntactic sugar changed decorator to context manager.
        """
        @functools.wraps(func)
        def inner(*args, **kwds):
            if self.__at is None: # this class is used as a decorator
                self.__at = f"{func.__module__}.{func.__qualname__}({reprArgs(*args, **kwds)})"
            with self._recreate_cm():
                return func(*args, **kwds)
        return inner
        
    def __enter__(self):
        r"""Enter method returns self for representation in with clause.
        """
        if self.__at is None: # this class is used as a context manager
            frameInfo = inspect.stack()[1]
            self.__at = f"with@{frameInfo.frame.f_globals.get('__name__')}:{frameInfo.lineno}"
        logger.log(self.__level, f'{self} entered')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        r"""Exit method retains its optional exception handling even when used as a decorator.
        """
        logger.log(self.__level, f'{self} exited' if exc_val is None else f'{self} raised: {exc_val!r}')
        return False

@contextlib.contextmanager
def context(logger, level=logging.DEBUG):
    r'''A context manager supports longging on code block begin and end with given logger, level and name.
    
    Deprecated, use `ContextDecorator` instead!
    '''
    frameInfo = inspect.stack()[2]
    ctx = f"with@{frameInfo.frame.f_globals.get('__name__')}:{frameInfo.lineno}"
    logger.log(level, f'{ctx} entered')
    try:
        yield ctx
    except Exception as exc:
        logger.log(level, f'{ctx} raised: {exc!r}')
        raise # otherwise the contextlib.contextmanager will indicate to exception has been handled
    else:
        logger.log(level, f'{ctx} exited')

def decorator(logger, level=logging.DEBUG):
    r'''A decorator wraps longging on function call's begin and end with given logger and level.
    
    Deprecated, use `ContextDecorator` instead!
    '''
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            at = f"{func.__module__}.{func.__qualname__}({reprArgs(*args, **kwds)})"
            logger.log(level, f'{at} entering')
            try:
                result = func(*args, **kwds)
            except Exception as exc:
                logger.log(level, f'{at} raised: {exc!r}')
                raise
            else:
                logger.log(level, f'{at} exited')
                return result
        return wrapper
    return inner

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(handler_color) # as app
    logger.setLevel(logging.DEBUG)
    
    logger.info('here we demonstrates')
    
    for each in (ContextDecorator, context):
        def f():
            try:
                with each(logger=logger) as ctx:
                    logger.info(f'now works in {ctx}')
                    raise RuntimeWarning('code block raised this exception')
                    print("this satement will never run!")
            except Exception as exc:
                logger.warning(f'caught exception: {reprExc(exc)}')
        f()
        
    for each in (ContextDecorator, decorator):
        try:
            @each(logger=logger)
            def f(a=1, b=2, *t, **d):
                logger.info(f'now works in some function')
                raise RuntimeWarning('exc raised in a function')
                return a+b
            f(10, 20, 30, z=100)
        except Exception as exc:
            logger.warning(f'caught exception: {reprExc(exc)}')
        
        
        