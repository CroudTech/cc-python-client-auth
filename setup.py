# -*- coding: utf-8 -*-
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require("setuptools>=38.3")
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

with open("requirements.txt") as f:
    required = f.read().splitlines()

if __name__ == "__main__":
    setup(
        install_requires=required,
        packages=["client_aith"],
    )