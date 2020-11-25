#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Package build script for setuptools.

See:
- https://packaging.python.org/tutorials/packaging-projects/
- https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import pathlib
import setuptools
import pyopg as pkg

setuptools.setup(
    name = pkg.__package__,
    version = pkg.__version__,
    author = pkg.__author__,
    author_email = "li.lei03@opg.cn",
    description = pkg.__doc__.splitlines()[0],
    long_description = (pathlib.Path(__file__).parent.resolve()/"README.md").read_text(encoding='utf-8'),
    long_description_content_type = "text/markdown",
    url = 'https://github.com/opgcn/pyopg',
    license_files = ['LICENSE'],
    packages = setuptools.find_packages(),
    python_requires = "~=" + pkg._pkg_py_ver,
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

