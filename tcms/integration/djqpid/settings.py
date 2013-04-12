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

# Plugin settings

'''
Configuration for QPID messaging
All settings contain sample value. You should modify them to make them apply to your project
'''

import os

# Enable or disable messaging in project
# If this is set to False, no messages will be sent from site
ENABLE_MESSAGING = True

# QPID configuration
QPID_BROKER_HOST = 'localhost'
QPID_BROKER_PORT = 5672
QPID_BROKER_SASL_MECHANISMS = ''
QPID_BROKER_TRANSPORT = 'tcp'

# If using GSSAPI for kerberos authentication, should set this to True
# When not using GSSAPI, MessageBus will ignore all Kerberos-related configuration
USING_GSSAPI = False

AUTH_USERNAME = ''
AUTH_PASSWORD = ''

# Kerberos configuration
SERVICE_KEYTAB = '/path/to/httpd/conf/httpd.keytab'
SERVICE_NAME = 'HTTP'
SERVICE_HOSTNAME = 'x.y.z'
REALM = 'COMPANY.COM'
# Accoding to the Kerberos V5 standard, the principal follows format servicename/hostname@REALM
SERVICE_PRINCIPAL = '%s/%s@%s' % (SERVICE_NAME, SERVICE_HOSTNAME, REALM)

# Messaging configuration

# For sending messages
EXCHANGE_NAME = 'amp.topic'
ROUTING_KEY_PREFIX = 'project_name'
# Sample address, youmight modify it for your project
SENDER_ADDRESS = '%s; { assert: always, node: { type: topic } }' % EXCHANGE_NAME

# For receiving messages
TMP_QUEUE_NAME = 'tmp.queue'
# X_BINDING_ITEMS is convenient for formatting multiple x-bindings items in receiver's address.
# If there is only one x-bindings item, you might not need to use this. Write it in address directly.
X_BINDING_ITEMS = (
    #'{ exchange: "%s", queue: "%s", key: "stock.#" }' % (EXCHANGE_NAME, TMP_QUEUE_NAME),
    #'{ exchange: "%s", queue: "%s", key: "weather.#" }' % (EXCHANGE_NAME, TMP_QUEUE_NAME),
)
# Sample address, you might modify it for your project
RECEIVER_ADDRESS = '''%s;
    {
        assert: always,
        create: receiver,
        node: {
            type: queue, durable: False,
            x-declare: {
                exclusive: True,
                auto_delete: True
            },
            x-bindings: [ %s ]
        }
    }'''.replace(os.linesep, '') % (
        TMP_QUEUE_NAME, ','.join(X_BINDING_ITEMS))
