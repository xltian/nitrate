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

import settings
from sender import QPIDSender
from tcms.core.models import signals

class QPIDProcessor(object):
    def __init__(self):
        self.settings = settings.PLUGIN_SETTINGS
        self.sender = QPIDSender(settings.URL, **settings.PLUGIN_SETTINGS)
    
    def __call__(self, data):
        return self.push(data)
    
    def push(self, data):
        content, properties = self.process_data(data)
        if content:
            self.sender.send(content = content, properties = properties)
    
    def process_data(self, data):
        model = data['model']
        instance = data['instance']
        signal = data['signal']
        content = model._meta.module_name.title()
        properties = instance.serialize()
        if signal == signals.create:
            content += ' create'
        elif signal == signals.update:
            content += ' update'
        elif signal == signals.delete:
            content += ' delete'
        else:
            return None, None
        return content, properties
