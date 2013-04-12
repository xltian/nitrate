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

def api_version(request):
    """
    Description: Return the API version of Nitrate.
    """
    from tcms import XMLRPC_VERSION
    return XMLRPC_VERSION
    
def testopia_version(request):
    """
    Description: Returns the version of Nitrate on this server.
    """
    from tcms import VERSION
    return VERSION

def nitrate_version(request):
    """
    Description: Returns the version of Nitrate on this server.
    """
    from tcms import VERSION
    return VERSION

def tcms_version(request):
    """
    Description: Returns the version of Nitrate on this server.
    """
    from tcms import VERSION
    return VERSION
