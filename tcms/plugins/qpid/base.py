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

import qpid
import qpid.messaging
import logging
from django.core import exceptions
logging.basicConfig()

class QPIDBase(object):
    def __init__(self, url=None, **options):
        """
        Creates a connection. A newly created connection must be connected
        with the Connection.connect() method before it can be used.
        
        @type url: str
        @param url: [ <username> [ / <password> ] @ ] <host> [ : <port> ]
        @type host: str
        @param host: the name or ip address of the remote host (overriden by url)
        @type port: int
        @param port: the port number of the remote host (overriden by url)
        @type transport: str 
        @param transport: one of tcp, tcp+tls, or ssl (alias for tcp+tls)
        @type heartbeat: int
        @param heartbeat: heartbeat interval in seconds
        
        @type username: str
        @param username: the username for authentication (overriden by url)
        @type password: str
        @param password: the password for authentication (overriden by url)
        
        @type sasl_mechanisms: str
        @param sasl_mechanisms: space separated list of permitted sasl mechanisms
        @type sasl_service: str
        @param sasl_service: ???
        @type sasl_min_ssf: ???
        @param sasl_min_ssf: ???
        @type sasl_max_ssf: ???
        @param sasl_max_ssf: ???
        
        @type reconnect: bool
        @param reconnect: enable/disable automatic reconnect
        @type reconnect_timeout: float
        @param reconnect_timeout: total time to attempt reconnect
        @type reconnect_internal_min: float
        @param reconnect_internal_min: minimum interval between reconnect attempts
        @type reconnect_internal_max: float
        @param reconnect_internal_max: maximum interval between reconnect attempts
        @type reconnect_internal: float
        @param reconnect_interval: set both min and max reconnect intervals
        @type reconnect_limit: int
        @param reconnect_limit: limit the total number of reconnect attempts
        @type reconnect_urls: list[str]
        @param reconnect_urls: list of backup hosts specified as urls
        
        @type address_ttl: float
        @param address_ttl: time until cached address resolution expires
        
        @rtype: Connection
        @return: a disconnected Connection
        """
        if not options.get('queue_name'):
            raise exceptions.ImproperlyConfigured('queue_name is required by QPID plugin.')
        self.queue_name = options['queue_name']
        self.url = url
        self.options = options
        self.connection = None
        self.session = None
        
    def init_connect(self):
        """Initial the connection"""
        self.connection = qpid.messaging.Connection(
            url = self.url, options = self.options
        )
        self.connection.open()
        
    def init_session(self):
        """Initial the session"""
        if not self.connection:
            self.init_connect()
        self.session = self.connection.session()
    
    def close(self):
        """Close the connection and session"""
        self.session.close()
        self.connection.close()
