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
#   Xuqing Kuang <xkuang@redhat.com>

"""
The XML-RPC is compatible with Testopia.
Only the arguments are different.

See https://wiki.mozilla.org/Testopia:Documentation:XMLRPC for testopia docs.
"""

__all__ = (
    'auth', 'build', 'testcase', 'testcaserun', 'testcaseplan', 'testopia', 'testplan',
    'testrun', 'user', 'version', 'tag',
)

XMLRPC_VERSION = (1, 1, 0, 'final', 1)

def get_version():
    return XMLRPC_VERSION
