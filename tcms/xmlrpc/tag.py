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
#   Jian Chen <jianchen@redhat.com>

from tcms.apps.management.models import TestTag

__all__ = ('get_tags', )

def get_tags(request, values):
    """
    Description:  Get the list of tags.

    Params:      $values - Hash: keys must match valid search fields.
        +------------------------------------------------------------+
        |                   tag Search Parameters                    |
        +------------------------------------------------------------+
        | Key                     | Valid Values                     |
        | ids                     | List of Integer                  |
        | names                   | List of String                   |
        +------------------------------------------------------------+

    Returns:     Array: An array of tag object hashes.

    Example:

    >>> values= {'ids': [121, 123]}
    >>> Tag.get_tags(values)
    """
    if values.get('ids'):
        query = {'id__in': values.get('ids')}
        return TestTag.to_xmlrpc(query)
    elif values.get('names'):
        query = {'name__in': values.get('names')}
        return TestTag.to_xmlrpc(query)
    else:
        raise
