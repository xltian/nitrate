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
# FIXME: Use logger to replace the function

from datetime import datetime

from django.conf import settings

DEBUG_NONE = 0
DEBUG_INFO = 1
DEBUG_ERROR = 5

def debug_output(message, level = DEBUG_INFO):
    if settings.DEBUG_LEVEL >= level and settings.DEBUG:
        if not hasattr(settings, 'DEBUG_LOG_FILE'):
            print "%s - %s: %s \n" % (str(datetime.now()), level, message)
            return
        
        try:
            debug_file = open(settings.DEBUG_LOG_FILE, 'wo+')
            debug_file.write("%s - %s: %s \n" % (str(datetime.now()), level, message))
            debug_file.close()
        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
        except ValueError:
            print "Value Error"
        except:
            import sys
            print "Unexpected error:", sys.exc_info()[0]
            raise

def debug_sql(msg):
    """
    Django doesn't seem to have a way to send all SQL to the standard
    logging deatures.  Instead, it has its own logging for SQL.
    (code is in django.db.backends.util.CursorDebugWrapper)


    This function lets you insert a message into the Django SQL log.

    It issues a dummy SQL query, that merely evaluates a string
    constant (your message), so that you can see this in the debug
    logs.
    """
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT %s", [msg])
