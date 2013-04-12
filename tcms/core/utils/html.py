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
# Stolen from http://djangosnippets.org/snippets/957/
# All right reserved by orignal authors.

from subprocess import Popen, PIPE

def html2text(value):
    """
    Pipes given HTML string into the text browser W3M, which renders it.
    Rendered text is grabbed from STDOUT and returned.
    """
    try:
        cmd = "w3m -dump -T text/html -O ascii"
        proc = Popen(cmd, shell = True, stdin = PIPE, stdout = PIPE)
        return proc.communicate(str(value))[0]
    except OSError:
        # something bad happened, so just return the input
        return value


if __name__ == "__main__":
    from urllib import urlopen
    print html2text(urlopen("http://www.w3.org/TR/REC-html40/").read())

