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
import functools, itertools, contextlib, inspect, logging

from . import color

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

def reprArgs(*t, **d):
    r'''Return arguments' representation string as in function invocation.
    '''
    return ','.join(itertools.chain( # chain generators, then join with comma
        map(repr, t),   # generator of positional arguments
        ( f'{k}={v!r}' for k, v in d.items() ), # generator of keyword arguments
    ))

def reprExc(exc):
    r"""Return a detailed representation string of an exception instance.
    """
    return f"{exc!r}<context={exc.__context__!r},suppress={exc.__suppress_context__!r},cause={exc.__cause__!r}>"

class Tracker(contextlib.ContextDecorator):
    r"""A tracker to log starting and finishing as a context manager or a decorator.

    Like https://docs.python.org/zh-cn/3/library/contextlib.html#using-a-context-manager-as-a-function-decorator , but both exceptions and function invocation details are included.
    Deprecated: use `context()` and `decorator()` respectivly.
    """
    def __init__(self, logger, level=logging.DEBUG, *t, **d):
        r"""Initialization.
        """
        self.__logger = logger
        self.__level = level
        self.__invocation = None
        super().__init__(*t, **d)

    def __str__(self):
        r"""Logging invocation string as <module>:<lineno> for context manager, and as <func>(<args>) for decorator.
        """
        return self.__invocation

    def __call__(self, func):
        r"""Syntactic sugar treats context manager as decorator.

        Note that there is one additional limitation when using context managers as function decorators: there's no way to access the return value of __enter__()
        """
        # __call__(func)(*t, **d) -> _wrapper(*t, **d)
        @functools.wraps(func)
        def _wrapper(*t, **d):
            if self.__invocation is None: # this class is used as a decorator
                self.__invocation = f"{func.__module__}.{func.__qualname__}({reprArgs(*t, **d)})"
            with self._recreate_cm():
                return func(*t, **d) # original func() is 'wrapped function'
        return _wrapper # from __call__()

    def __enter__(self):
        r"""Enter method returns self for representation in with clause.
        """
        if self.__invocation is None: # this class is used as a context manager
            frameInfo = inspect.stack()[1]
            self.__invocation = f"with@{frameInfo.frame.f_globals.get('__name__')}:{frameInfo.lineno}"
        logger.log(self.__level, f'{self} entering')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        r"""Exit method retains its optional exception handling even when used as a decorator.
        """
        logger.log(self.__level, f'{self} exited' if exc_val is None else f'{self} raised: {exc_val!r}')
        return False

@contextlib.contextmanager
def context(logger, level=logging.DEBUG):
    r'''A context manager supports longging on code block begin and end with given logger, level and name.
    '''
    frameInfo = inspect.stack()[2]
    ctx = f"with@{frameInfo.frame.f_globals.get('__name__')}:{frameInfo.lineno}"
    logger.log(level, f'{ctx} entered')
    try:
        yield ctx
    except Exception as exc:
        logger.log(level, f'{ctx} raised: {reprExc(exc)}')
        raise # otherwise the contextlib.contextmanager will indicate to exception has been handled
    else:
        logger.log(level, f'{ctx} exited')

def decorator(logger, level=logging.DEBUG):
    r'''A decorator wraps longging on function call's begin and end with given logger and level.
    '''
    # decorator(logger)(func)(*t, **d) -> _inner_decorator(func)(*t, **d) -> _wrapper(*t, **d)
    def _inner_decorator(func):
        @functools.wraps(func)
        def _wrapper(*t, **d):
            invocation = f"{func.__module__}.{func.__qualname__}({reprArgs(*t, **d)})"
            logger.log(level, f'{invocation} starting')
            try:
                result = func(*t, **d) # original func() is 'wrapped function'
            except Exception as exc:
                logger.log(level, f'{invocation} raised: {reprExc(exc)}')
                raise
            else:
                logger.log(level, f'{invocation} returned: {result!r}')
                return result # from _wrapper()
        return _wrapper # from _inner_decorator()
    return _inner_decorator # from decorator()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(handler_color) # as app
    logger.setLevel(logging.DEBUG)

    logger.info('here we go demos')

    logger.info('now demonstrates context manager')
    def f():
        try:
            with context(logger=logger) as ctx:
                logger.info(f'now works in {ctx}')
                raise RuntimeWarning('code block raised this exception')
                print("this satement will never run!")
        except Exception as exc:
            logger.warning(f'caught exception: {reprExc(exc)}')
    f()

    logger.info('now demonstrates decorator')
    try:
        @decorator(logger=logger)
        def f(a=1, b=2, *t, **d):
            r"""This is some function.
            """
            logger.info(f'now works in some function')
            raise RuntimeWarning('exc raised in a function')
            return a+b
        logger.info(f'__name__ of f() is {f.__name__!r}')
        f(10, 20, 30, z=100)
    except Exception as exc:
        logger.warning(f'caught exception: {reprExc(exc)}')

    logger.info('here we finished demonstration')
