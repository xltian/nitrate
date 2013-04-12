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
#   Chaobin Tang <ctang@redhat.com>

'''
Print result of cProfile in a file
'''

import sys
import os

def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        raise SystemExit('Specify the filename')
    else:
        print_stats(filename)

def print_stats(filename):
    import pstats
    stats = pstats.Stats(filename)
    stats = stats.sort_stats('cumulative')
    stats.print_stats()

if __name__ == '__main__':
    main()
