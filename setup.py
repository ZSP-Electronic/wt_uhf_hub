#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
                    'Adafruit-BBIO>=1.0.10',
                    'google-cloud-datastore>=1.4.0',
                    'google-cloud-storage>=1.6.0',
                    'numpy>=1.13.3',
                    'pyserial>=3.4',
                    'PyBOMBS>=2.3.2',
                    'python-smbus>=3.1.2'
                    # TODO: Put package requirements here
                ]

setup(
    name='wt_uhf_hub',
    version='0.9.1',
    long_description=readme + '\n\n' + history,
    author="Zachary Pina",
    author_email='zacharypina@gmail.com',
    url='https://github.com/ZSPina/wt_uhf_hub',
    packages=find_packages(exclude=['docs', 'tests', 'venv']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='wt_uhf_hub',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
)
