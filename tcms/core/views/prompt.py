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
# FIXME: Use exception to replace the feature

class Prompt(object):
    """Common dialog to prompt to users"""
    Alert = 'alert'
    Info = 'info'
    
    def __init__(self, request, info_type = None, info = None, next = None):
        super(Prompt, self).__init__()
        self.request = request
        self.info_type = info_type
        self.info = info
        self.next = next
        
    #def __repr__(self):
    #    return self.html
    
    @classmethod
    def render(cls, request, info_type = None, info = None, next = None):
        """Generate the html to response"""
        from django.template import RequestContext, loader
        
        t = loader.get_template('prompt.html')
        c = RequestContext(request, {
            'type': info_type,
            'info': info,
            'next': next
        })
        
        return t.render(c)
