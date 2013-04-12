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
#
# Plugin settings
# Please see the doc in based.py or Connection.__init__() function from qpid-python.
# https://svn.apache.org/repos/asf/qpid/trunk/qpid/python/qpid/messaging/endpoints.py
# The argument is same with it.

URL = 'amqp://guest/guest@10.66.93.193:5672'

PLUGIN_SETTINGS = {
    'host': 'amqp://guest/guest@10.66.93.193:5672', # Buggy here, the argument can't use
    'username': 'guest',
    'password': 'guest',
    'queue_name': 'message_queue',
    'sasl_mechanisms': 'PLAIN',
    'heartbeat': 5,
    'reconnect': True,
    'reconnect_timeout': 10,
    'reconnect_limit': 5,
}
