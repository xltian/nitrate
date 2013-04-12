# -*- coding: utf-8 -*-
# 
# Nitrate is copyright 2010 Red Hat, Inc.
# 
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
# 
# Authors:
#   David Malcolm <dmalcolm@redhat.com>
#   Xuqing Kuang <xkuang@redhat.com>

import os
import sys
import tcms
from setuptools import setup, find_packages

PACKAGE_NAME = 'Nitrate'
PACKAGE_VER = '3.3.4'
PACKAGE_DESC = 'Test Case Management System'
PACKAGE_URL = 'https://fedorahosted.org/nitrate/browser/trunk/nitrate'

def get_files_below(path):
    # we need to generate a list of paths to static files
    # We have been invoked from "build".
    # The files we need are in "build/tcms/static"
    # The paths must be relative to "tcms"
    # Therefore we add a "tcms" to os.walk, and strip off the leading "tcms" at the end:
    for (dirpath, dirnames, filenames) in os.walk(os.path.join('tcms', path)):
        for filename in filenames:
            # strip off leading "tcms/" string from each path:
            yield os.path.join(dirpath, filename)[5:]
        
def get_package_data():
    # annoyingly, it appears that package_data has to list filenames; it can't
    # cope with directories, so we have to figure this out for it:
    result = {
        '': [] + list(get_files_below('../templates')) + list(get_files_below('../media')) + list(get_files_below('../docs')),
    }
    return result

setup(
    name = PACKAGE_NAME,
    version = PACKAGE_VER,
    description = PACKAGE_DESC,
    url = PACKAGE_URL,
    packages=find_packages(exclude='tests'),
    # package_data=get_package_data(),
    install_requires=[
        'Django==1.2',
        'kobo',
        'MySQL-python',
        'kerberos',
        'python-memcached',
        'django-pagination',
        'django-tinymce',
        'wadofstuff-django-serializers',
        'xml2dictnitrate',
        'qpid-python',
        'lxml',
    ],
)

