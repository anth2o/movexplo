#!/usr/bin/env python
from setuptools import setup

with open('requirements.txt') as f:
    packages = f.read().splitlines()

packages = [package for package in packages if not package.startswith("-e .")]

setup(install_requires=packages)
