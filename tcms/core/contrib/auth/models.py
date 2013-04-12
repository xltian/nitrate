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

from django.db import models

class UserActivateKey(models.Model):
    user = models.ForeignKey('auth.User')
    activation_key = models.CharField(max_length=40, null=True, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = u'tcms_user_activate_keys'
    
    @classmethod
    def set_random_key_for_user(cls, user, force = False):
        import random
        import datetime
        try:
            from hashlib import sha1
        except ImportError:
            from sha import new as sha1
        
        salt = sha1(str(random.random())).hexdigest()[:5]
        activation_key = sha1(salt+user.username).hexdigest()
        
        # Create and save their profile                                                                                                                                 
        k, c = cls.objects.get_or_create(user=user)
        if c or force:
            k.activation_key = activation_key
            k.key_expires = datetime.datetime.today() + datetime.timedelta(7)
            k.save()
        
        return k
