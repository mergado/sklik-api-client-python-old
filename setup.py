# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='sklikapi',
    version='1.0.0',
    author='Eduard Veleba, Michal Wiglasz, Pavel Dedik',
    description=('Python library for easier access to the Sklik.cz API,'
                 'a pay-per-click advertising system, operated by Seznam.cz.'),
    packages=find_packages(exclude=['tests']),
    install_requires=[],
    tests_require=[],
    include_package_data=True,
)
