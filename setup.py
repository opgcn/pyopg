#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Package build script for setuptools.

See https://packaging.python.org/tutorials/packaging-projects/ 
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import setuptools
import pyopg as pkg

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name = pkg.__package__,
    version = pkg.__version__,
    author = pkg.__author__,
    author_email = "li.lei03@opg.cn",
    description = pkg.__doc__.splitlines()[0],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/opgcn/pyopg',
    packages = setuptools.find_packages(),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
    ],
)