# -*- coding: utf-8 -*-

from tcms.xmlrpc import get_version

__all__ = (
    'get',
)

def get(request):
    '''
    Description: Retrieve XMLRPC's version

    Params:      No parameters.

    Returns:     A list that represents the version.

    Example:
    >>> Version.get()
    '''

    return get_version()
