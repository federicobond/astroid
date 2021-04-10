#!/usr/bin/env python
# Copyright (c) 2006, 2009-2010, 2012-2013 LOGILAB S.A. (Paris, FRANCE) <contact@logilab.fr>
# Copyright (c) 2010-2011 Julien Jehannet <julien.jehannet@logilab.fr>
# Copyright (c) 2014-2016, 2018-2020 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2014 Google, Inc.
# Copyright (c) 2017 Hugo <hugovk@users.noreply.github.com>
# Copyright (c) 2018-2019 Ashley Whetter <ashley@awhetter.co.uk>
# Copyright (c) 2019 Enji Cooper <yaneurabeya@gmail.com>
# Copyright (c) 2020-2021 hippo91 <guillaume.peillex@gmail.com>
# Copyright (c) 2020 David Gilman <davidgilman1@gmail.com>
# Copyright (c) 2020 Colin Kennedy <colinvfx@gmail.com>
# Copyright (c) 2021 Pierre Sassoulas <pierre.sassoulas@gmail.com>
# Copyright (c) 2021 Marc Mueller <30130371+cdce8p@users.noreply.github.com>

# Licensed under the LGPL: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
# For details: https://github.com/PyCQA/astroid/blob/master/LICENSE

"""Setup script for astroid."""
import os
import sys
from setuptools import find_packages, setup

real_path = os.path.realpath(__file__)
astroid_dir = os.path.dirname(real_path)


# pylint: disable=redefined-builtin; why license is a builtin anyway?
mailinglist = "mailto://%s" % "code-quality@python.org"
with open(os.path.join(astroid_dir, "README.rst")) as fobj:
    long_description = fobj.read()


needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
setup(
    name="astroid",
    version="2.6.0",
    license="LGPL-2.1-or-later",
    description="An abstract syntax tree for Python with inference support.",
    long_description=long_description,
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    author="Python Code Quality Authority",
    author_email="code-quality@python.org",
    url="https://github.com/PyCQA/astroid",
    python_requires=">=3.6",
    install_requires=[
        "lazy_object_proxy>=1.4.0",
        "wrapt>=1.11,<1.13",
        'typed-ast>=1.4.0,<1.5;implementation_name== "cpython" and python_version<"3.8"',
    ],
    extras_require={},
    packages=find_packages(exclude=["tests"]) + ["astroid.brain"],
    setup_requires=["pytest-runner"] if needs_pytest else [],
    test_suite="test",
    tests_require=["pytest"],
)
