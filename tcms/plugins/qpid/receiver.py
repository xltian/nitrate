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

from pprint import pprint
from base import QPIDBase

class QPIDReceiver(QPIDBase):
    def __init__(self, url, **kwargs):
        super(QPIDReceiver, self).__init__(url, **kwargs)
        self.receiver = None
    
    def init_receiver(self):
        """Initial the receiver"""
        if not self.session:
            self.init_session()
        self.receiver = self.session.receiver(self.queue_name)
        
    def receive(self):
        """Listing the messages from server"""
        if not self.receiver:
            self.init_receiver()
            
        try:
            while True:
                message = self.receiver.fetch()
                content = message.content
                pprint({'props': message.properties})
                pprint(content)
                self.session.acknowledge(message)
        except KeyboardInterrupt:
            pass
        
        self.close()

# Test code
if __name__ == '__main__':
    r = QPIDReceiver()
    r.receive()
