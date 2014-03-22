# -*- coding: utf-8 -*-
##
## This file is part of End-to-End Latency Analyzer for ProCom (EELAP).
## Copyright (C) 2012, 2013, 2014 Jiri Kuncar <jiri.kuncar@gmail.com>.
##
## EELAP is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## EELAP is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os
import re

from setuptools import setup

# Get the version string.  Cannot be done with import!
with open(os.path.join('eelap', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

install_requires = [
    'setuptools',
    'numpy',
    'lxml',
    'sphinxcontrib-bibtex',
    'sphinxcontrib-programoutput',
    # -*- Extra requirements: -*-
]

entry_points = {
    'console_scripts': [
        'eelap_generator = eelap.generator:main'
    ]
}


classifiers = [
    'Programming Language :: Python',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.md") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(
    name='EELAP',
    version=version,
    license='GPLv2',
    packages=['eelap'],
    description=("End-to-End Latency Analysis for ProCom"),
    long_description=README + '\n' + CHANGES,
    author='Jiri Kuncar',
    author_email='jiri.kuncar@gmail.com',
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=install_requires,
    keywords='latency analysis ProCom',
    url='https://github.com/jirikuncar/eelap/',
    entry_points=entry_points,
    test_suite='nose.collector',
    tests_require=['nose', 'coverage', 'httpretty'],
)
