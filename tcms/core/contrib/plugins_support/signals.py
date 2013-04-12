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
# The codes is references from django-fullhistory
# http://code.google.com/p/fullhistory/source/browse/trunk/fullhistory/fullhistory.py

from django.db.models import signals
from tcms.core.models import signals as tcms_signals
from processors import pstp

# Intial the regiested models
REGISTERED_MODELS = {}

# The global signal processor
class GlobalSignalProcessor(object):
    '''
    This class is responsible for handling all of signals trigger by model
    '''
    def __init__(self, model):
        self.model = model
    
    def initial_processor(self, entry):
        pstp.push(self.model, entry, tcms_signals.initial)
    
    def save_processor(self, entry, created):
        if created:
            pstp.push(self.model, entry, tcms_signals.create)
        pstp.push(self.model, entry, tcms_signals.update)
    
    def delete_processor(self, entry):
        pstp.push(self.model, entry, tcms_signals.delete)
    
    def apply_parents(self, instance, func):
        '''
        Iterates through all non-abstract inherited parents and applies the supplied function
        '''
        for field in instance._meta.parents.values():
            if field and getattr(instance, field.name, None):
                func(getattr(instance, field.name))

# The signal handlers
def initial_signal_handler(instance, **kwargs):
    if instance.pk is not None:
        handler = REGISTERED_MODELS[type(instance)]
        handler.initial_processor(instance)
        handler.apply_parents(instance, handler.initial_processor)

def save_signal_handler(instance, created, **kwargs):
    REGISTERED_MODELS[type(instance)].save_processor(instance, created)

def delete_signal_handler(instance, **kwargs):
    REGISTERED_MODELS[type(instance)].delete_processor(instance)

# Bind the signals and the models
def register_model(model, sp=None):
    if model in REGISTERED_MODELS:
        return
    for parent in model._meta.parents.keys():
        register_model(parent, cls)
    if sp is None:
        sp = GlobalSignalProcessor
    signals.post_init.connect(initial_signal_handler, sender=model)
    signals.post_save.connect(save_signal_handler, sender=model)
    signals.post_delete.connect(delete_signal_handler, sender=model)
    REGISTERED_MODELS[model] = sp(model)
