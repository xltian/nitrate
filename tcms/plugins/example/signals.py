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
# 
# Authors:
#   Xuqing Kuang <xkuang@redhat.com>

from pprint import pprint

class PrintMe(object):
    def __init__(self):
        pass
        
    def __call__(self, args):
        return self.print_me(args)
    
    def print_me(self, args):
        pprint(args)
