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

from . import log
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
class DataDescriptor:
    r'''A data-descriptor with default-value, logging abilities.

    - https://docs.python.org/zh-cn/3/reference/datamodel.html#descriptors
    - https://docs.python.org/zh-cn/3/howto/descriptor.html
    - https://www.python.org/dev/peps/pep-0252/#specification-of-the-attribute-descriptor-api
    - https://zhuanlan.zhihu.com/p/104727422
    '''

    # flag to disable abilities
    DISABLE = object()

    def __init__(self, default=DISABLE, doc=None, logger=None, level=logging.DEBUG):
        r'''Initialize with default value.
        '''
        self.__default = default
        self.__objclass__, self.__name__, self.__doc__ = None, None, doc # PEP-252
        self.__logger, self.__level = logger, level

    def __set_name__(self, owner, name):
        r"""Called at the time the owning class owner is created. The descriptor has been assigned to name.
        """
        self.__objclass__, self.__name__ = owner, name
        self._check_set_name()
        if self.__doc__ is None:
            self.__doc__ = repr(self)
        if self.__logger:
            self.__logger.log(self.__level, f"{self} constructed")

    def _check_set_name(self):
        r"""Check self.__set_name__() is called.

        __set_name__() is only called implicitly as part of the type constructor, so it will need to be called explicitly with the appropriate parameters when a descriptor is added to a class after initial creation.
        """
        if None in (self.__objclass__, self.__name__):
            raise AttributeError(f"{self.__class__.__qualname__}().__set_name__() not worked appropriatly!")

    def __repr__(self):
        r"""Representation as '<OwnerName.AttributeName=SelfClassName(ImportantArgs)>'.
        """
        dArgs = dict()
        if self.__default is not self.DISABLE:
            dArgs['default'] = self.__default
        return f"<{self.__objclass__.__qualname__}.{self.__name__}={self.__class__.__qualname__}({log.reprArgs(**dArgs)})>"

    def __get__(self, instance, owner=None):
        self._check_set_name()
        if self.__logger:
            dArgs = {'instance':instance, 'owner':owner}
            self.__logger.log(self.__level, f'{self} excuting __get__({log.reprArgs(**dArgs)})')
        if instance is None: # class-binding access
            return self
        try:
            return instance.__dict__[self]
        except KeyError as exc:
            if self.__default is self.DISABLE:
                raise AttributeError(f"{self} not found for instance {instance!r}") from None
            return self.__default

    def __set__(self, instance, value):
        self._check_set_name()
        if self.__logger:
            dArgs = {'instance':instance, 'value':value}
            self.__logger.log(self.__level, f'{self} excuting __set__({log.reprArgs(**dArgs)})')
        instance.__dict__[self] = value

    def __delete__(self, instance):
        self._check_set_name()
        if self.__logger:
            dArgs = {'instance':instance}
            self.__logger.log(self.__level, f'{self} excuting __delete__({log.reprArgs(**dArgs)})')
        try:
            del instance.__dict__[self]
        except KeyError as exc:
            raise AttributeError(f"{self} not found for instance {instance!r}") from None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # demonstrates utils
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler()) # as lib
    logger.addHandler(log.handler_color) # as app
    logger.setLevel(logging.DEBUG)

    logger.info("now demonstrates DataDescriptor's construction")
    class C:
        a = DataDescriptor(logger=logger, doc='this is a')
        b = DataDescriptor(logger=logger, default='$default-value-of-b$')
    c = C()
    logger.info(f"C.__dict__={C.__dict__}")
    logger.info(f"c.__dict__={c.__dict__}")

    logger.info("now demonstrates DataDescriptor's non-default non-set-yet access")
    try:
        c.a
    except Exception as exc:
        logger.warning(f"caught exception: {log.reprExc(exc)}")

    logger.info("now demonstrates DataDescriptor's non-set-yet deletion")
    try:
        del c.b
    except Exception as exc:
        logger.warning(f"caught exception: {log.reprExc(exc)}")

    logger.info("now demonstrates DataDescriptor's normal access")
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

    logger.info("now demonstrates DataDescriptor's deletion")
    del c.b
    logger.info(f"get c.b is {c.b!r}")
    logger.info(f"now c.__dict__={c.__dict__}")
    del C.a
    logger.info(f"after `del C.a` now C.__dict__={C.__dict__}")
    logger.info(f"now c.__dict__={c.__dict__}")
    try:
        C.a
    except Exception as exc:
        logger.warning(f"access 'C.a' caught exception: {log.reprExc(exc)}")
