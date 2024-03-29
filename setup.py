# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='sklikapi',
    version='2.0.4',
    author='Eduard Veleba, Michal Wiglasz, Pavel Dedik, Lukas Sevcik',
    description=('Python library for easier access to the Sklik.cz API,'
                 'a pay-per-click advertising system, operated by Seznam.cz.'),
    packages=find_packages(exclude=['tests']),
    install_requires=[],
    tests_require=[],
    include_package_data=True,
    test_suite="tests",
)
