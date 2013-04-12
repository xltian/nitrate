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

from tcms.apps.management.models import TestAttachment, TestAttachmentData
import datetime

def handle_uploaded_file(f, submitter_id, ):
    # Write to a temporary file
    dest = open('/tmp/' + f.name, 'wb+')
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()

    # Write the file to database
    file = open('/tmp' + f.name, 'ro')
    ta = TestAttachment.objects.create(
        submitter_id = submitter_id,
        description = None,
        filename = f.name,
        creation_ts = datetime.datetime.now()
    )
    return dest.name
