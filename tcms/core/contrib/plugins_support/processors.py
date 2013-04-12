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

import threading
from django.conf import settings
from django.utils.importlib import import_module

class NewThread(threading.Thread):
    def __init__(self, command, args):
        self.command = command
        self.args = args
        super(NewThread, self).__init__()
    
    def run(self):
        # The actual code we want to run
        return self.command(self.args)

class PushSignalToPlugins(object):
    def __init__(self):
        self.plugins = []
        
    def import_plugins(self):
        if not hasattr(settings, 'SIGNAL_PLUGINS') or not settings.SIGNAL_PLUGINS:
            return
        
        for p in settings.SIGNAL_PLUGINS:
            self.plugins.append(import_module(p))
    
    def push(self, model, instance, signal):
        for p in self.plugins:
            NewThread(p.receiver, {'model': model, 'instance': instance, 'signal': signal}).start()

# Create the PushSignalToPlugins instance
pstp = PushSignalToPlugins()
pstp.import_plugins()
