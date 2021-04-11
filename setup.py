import os.path

from setuptools import setup

pkginfo = os.path.join(os.path.dirname(__file__), "astroid", "__pkginfo__.py")

with open(pkginfo, "rb") as fobj:
    exec(compile(fobj.read(), pkginfo, "exec"), locals())  # pylint: disable=exec-used

setup(version=__version__)  # pylint: disable=undefined-variable
