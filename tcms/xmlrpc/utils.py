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

from tcms.apps.management.models import Product

def pre_check_product(values):
    if isinstance(values, dict):
        if not values.get('product'):
            return
        product_str = values['product']
    else:
        product_str = values

    if not (isinstance(product_str, str) or isinstance(product_str, int)):
        raise ValueError('The type of product is not recognizable.')

    try:
        product_id = int(product_str)
        return Product.objects.get(id = product_id)
    except ValueError:
       return Product.objects.get(name = product_str)

def pre_process_ids(value):
    if isinstance(value, list):
        return [isinstance(c, int) and c or int(c.strip()) for c in value if c]

    if isinstance(value, str):
        return [int(c.strip()) for c in value.split(',') if c]

    if isinstance(value, int):
        return [value]

    raise TypeError('Unrecognizable type of ids')

def compare_list(src_list, dest_list):
    return list(set(src_list)-set(dest_list))

class Comment(object):
    def __init__(self, request, content_type, object_pks, comment = None):
        self.request = request
        self.content_type = content_type
        self.object_pks = object_pks
        self.comment = comment

    def add(self):
        import time
        from django.db import models
        from django.contrib import comments
        from django.contrib.comments.views.comments import CommentPostBadRequest
        from django.contrib.comments import signals

        comment_form = comments.get_form()

        try:
            model = models.get_model(*self.content_type.split('.', 1))
            targets = model._default_manager.filter(pk__in = self.object_pks)
        except:
            raise

        for target in targets:
            d_form = comment_form(target)
            timestamp = str(time.time()).split('.')[0]
            object_pk = str(target.pk)
            data = {
                'content_type': self.content_type,
                'object_pk': object_pk,
                'timestamp': timestamp,
                'comment': self.comment
            }
            security_hash_dict = {
                'content_type': self.content_type,
                'object_pk': object_pk,
                'timestamp': timestamp
            }
            data['security_hash'] = d_form.generate_security_hash(**security_hash_dict)
            form = comment_form(target, data=data)

            # Response the errors if got
            if not form.is_valid():
                return form.errors

            # Otherwise create the comment
            comment = form.get_comment_object()
            comment.ip_address = self.request.META.get("REMOTE_ADDR", None)
            if self.request.user.is_authenticated():
                comment.user = self.request.user

            # Signal that the comment is about to be saved
            responses = signals.comment_will_be_posted.send(
                sender  = comment.__class__,
                comment = comment,
                request = self.request
            )

            # Save the comment and signal that it was saved
            comment.save()
            signals.comment_was_posted.send(
                sender  = comment.__class__,
                comment = comment,
                request = self.request
            )

        return
