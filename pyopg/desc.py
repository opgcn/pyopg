#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Utilities for descriptor.

This module provides descriptor utils for human beings.
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

from . import __version__, __author__, __date__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import logging

from . import debug, log
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DataDesc:
    r'''A data descriptor with default-value, logging abilities.

    - https://docs.python.org/zh-cn/3/reference/datamodel.html#descriptors
    - https://docs.python.org/zh-cn/3/howto/descriptor.html
    - https://www.python.org/dev/peps/pep-0252/#specification-of-the-attribute-descriptor-api
    - https://zhuanlan.zhihu.com/p/104727422
    '''

    # flag to disable abilities
    DISABLE = object()

    def __init__(self, default=DISABLE, doc=None, logger=None, level=logging.DEBUG, actual_prefix='__'):
        r'''Initialize with default value.
        '''
        self._default = default
        self.__objclass__, self.__name__, self.__doc__ = None, None, doc # PEP-252
        self._actual_prefix = actual_prefix # https://docs.python.org/zh-cn/3/howto/descriptor.html#managed-attributes
        self._logger, self._level = logger, level

    def __set_name__(self, owner, name):
        r"""Called at the time the owning class owner is created. The descriptor has been assigned to name.
        """
        self.__objclass__, self.__name__ = owner, name
        self._check_set_name()
        self._name = self._actual_prefix + name # actual data stored as a private attribute in instance dictionary
        if self.__doc__ is None:
            self.__doc__ = repr(self)
        if self._logger:
            self._logger.log(self._level, f"{self} constructed")

    def _check_set_name(self):
        r"""Check self.__set_name__() is called.

        __set_name__() is only called implicitly as part of the type constructor, so it will need to be called explicitly with the appropriate parameters when a descriptor is added to a class after initial creation.
        """
        if None in (self.__objclass__, self.__name__):
            raise AttributeError(f"{self.__class__.__qualname__}().__set_name__() not worked appropriatly!")

    def __repr__(self):
        r"""Representation.
        """
        if self._default is self.DISABLE:
            return debug.reprDesc(self)
        else:
            return debug.reprDesc(self, default=self._default)

    def __get__(self, instance, owner=None):
        self._check_set_name()
        if self._logger:
            self._logger.log(self._level, f'{debug.reprSelfMethod(self.__get__, instance=instance, owner=owner)} excuting')
        if instance is None: # class-binding access
            return self
        elif self._default is self.DISABLE:
            return getattr(instance, self._name)
        else:
            return getattr(instance, self._name, self._default)

    def __set__(self, instance, value):
        self._check_set_name()
        if self._logger:
            dArgs = {'instance':instance, 'value':value}
            self._logger.log(self._level, f'{debug.reprSelfMethod(self.__set__, instance=instance, value=value)} excuting')
        setattr(instance, self._name, value)

    def __delete__(self, instance):
        self._check_set_name()
        if self._logger:
            dArgs = {'instance':instance}
            self._logger.log(self._level, f'{debug.reprSelfMethod(self.__delete__, instance=instance)} excuting')
        delattr(instance, self._name)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(log.handler_color) # as app
    logger.setLevel(logging.DEBUG)

    logger.info("now demonstrates DataDesc's construction")
    class C:
        a = DataDesc(logger=logger, doc='this is a')
        b = DataDesc(logger=logger, default='$default-value-of-b$')
    c = C()
    logger.info(f"C.__dict__={C.__dict__}")
    logger.info(f"c.__dict__={c.__dict__}")

    logger.info("now demonstrates DataDesc's non-default non-set-yet access")
    try:
        c.a
    except Exception as exc:
        logger.warning(f"caught exception: {debug.reprExc(exc)}")

    logger.info("now demonstrates DataDesc's non-set-yet deletion")
    try:
        del c.b
    except Exception as exc:
        logger.warning(f"caught exception: {debug.reprExc(exc)}")

    logger.info("now demonstrates DataDesc's normal access")
    c.a = 10
    logger.info(f"get c.a is {c.a!r}")
    logger.info(f"get c.b is {c.b!r}")
    logger.info(f"now c.__dict__={c.__dict__}")
    c.b = 20
    logger.info(f"get c.b is {c.b!r}")
    logger.info(f"now c.__dict__={c.__dict__}")
    c.a = 'updated-to-100'
    logger.info(f"get c.a is {c.a!r}")
    logger.info(f"now c.__dict__={c.__dict__}")
    logger.info(f"get C.a is {C.a!r}")

    logger.info("now demonstrates DataDesc's deletion")
    del c.b
    logger.info(f"get c.b is {c.b!r}")
    logger.info(f"now c.__dict__={c.__dict__}")
    del C.a
    logger.info(f"after `del C.a` now C.__dict__={C.__dict__}")
    logger.info(f"now c.__dict__={c.__dict__}")
    try:
        C.a
    except Exception as exc:
        logger.warning(f"access 'C.a' caught exception: {debug.reprExc(exc)}")
        
