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
from django.http import HttpResponse
from django.utils import simplejson
from django.views.generic.simple import direct_to_template

from django.contrib import comments
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.comments import signals

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required

from tcms import settings

def all(request, template_name='comments/comments.html'):
    """
    List the comment of a specific object
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.REQUEST.copy()
     
    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except:
        raise
    
    return direct_to_template(request, template_name, {
        'object': target,
    })

def post(request, template_name='comments/comments.html'):
    """
    Post a comment.
    
    HTTP POST is required.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except:
        raise
    
    # Construct the comment form
    form = comments.get_form()(target, data=data)
    if not form.is_valid():
        return direct_to_template(request, template_name, {
            'object': target,
            'form': form,
        })
    
    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user
    
    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    
    # Save the comment and signal that it was saved
    comment.is_removed = False
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    
    return direct_to_template(request, template_name, {
        'object': target,
        'form': form,
    })

#@permission_required("comments.delete_comment")
def delete(request, next=None):
    """
    Deletes a comment. Confirmation on GET, action on POST. Requires the "can
    moderate comments" permission.
    """
    from django.conf import settings
    
    ajax_response = {'rc': 0, 'response': 'ok'}
    comments_s = comments.get_model().objects.filter(
        pk__in = request.REQUEST.getlist('comment_id'),
        site__pk = settings.SITE_ID
    )
    
    if not comments_s:
        if request.is_ajax():
            ajax_response = {'rc': 1, 'response': 'Object does not exist.'}
            return HttpResponse(simplejson.dumps(ajax_response))
        
        raise ObjectDoesNotExist()
    
    # Delete on POST
    # Flag the comment as deleted instead of actually deleting it.
    for comment in comments_s:
        if comment.user == request.user:
            flag, created = comments.models.CommentFlag.objects.get_or_create(
                comment = comment,
                user    = request.user,
                flag    = comments.models.CommentFlag.MODERATOR_DELETION
            )
            comment.is_removed = True
            comment.save()
            signals.comment_was_flagged.send(
                sender  = comment.__class__,
                comment = comment,
                flag    = flag,
                created = created,
                request = request,
            )
    

    return HttpResponse(simplejson.dumps(ajax_response))
    #return next_redirect(request.POST.copy(), next, delete_done, c=comment.pk)
delete = permission_required("comments.can_moderate")(delete)
