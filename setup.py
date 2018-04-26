#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name='chpro',
    version='1.0',
    description='Dashboards for RapidPro for Health',
    long_description='',
    author='Nicolas Lara',
    author_email='nicolas@lincolnloop.com',
    url='https://github.com/rapidpro/chpro/',
    packages=find_packages(),
    scripts=[
        'chpro/bin/chpro'
    ],
    include_package_data=True,
)
