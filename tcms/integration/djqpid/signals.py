# -*- coding: utf-8 -*-
# 
# Nitrate internal plugin is copyright 2010 Red Hat, Inc.
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

from tcms.integration.djqpid.settings import ENABLE_MESSAGING

'''
Message Bus is controlled by ENABLE_MESSAGING variable defined in settings.
If the messaging is not enabled, no signal will be registered here.
'''

if ENABLE_MESSAGING:

    '''
    Register signals here. These signal handler will
    handle the message sending and the related data
    '''

    # TODO: add signal handler here
