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

import qpid.messaging
from datetime import datetime
from base import QPIDBase

class QPIDSender(QPIDBase):
    def __init__(self, url, **kwargs):
        super(QPIDSender, self).__init__(url, **kwargs)
        self.sender = None
    
    def init_sender(self):
        """Initial the sender"""
        if not self.session:
            self.init_session()
        self.sender = self.session.sender(self.queue_name)
    
    def send(self, content, properties = {}):
        """Sending the content"""
        if not self.sender:
            self.init_sender()
        message = qpid.messaging.Message(properties=properties, content = content)
        self.sender.send(message)
    
    def typing(self):
        """Sending the contents real time with typing"""
        content = ''
        while content != 'EOF':
            content = raw_input('Start typing:')
            self.send(content)

if __name__ == '__main__':
    s = QPIDSender()
    s.send('Testing at %s' % datetime.now())
    s.close()
