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
#   Xuqing Kuang <xkuang@redhat.com> Chaobin Tang <ctang@redhat.com>

# from django
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template import loader, Context, RequestContext

# from stdlib
import threading

def mailto(template_name, subject, to_mail, context = None, request = None, from_mail = None):
    """
    Based on Django's send_mail, to send notify email
    
    Arguments:
        template = the template of mail
        to_mail = to someone's email address
        subject = define the subject of the mail
        context = Context to render the mail content
    """
    try:
        t = loader.get_template(template_name)
        if request:
            mail_content = t.render(RequestContext(request, context))
        else:
            mail_content = t.render(Context(context))
        
        send_mail(settings.EMAIL_SUBJECT_PREFIX + subject,
                  mail_content, 
                  from_mail or settings.EMAIL_FROM,
                  isinstance(to_mail, list) and list(set(to_mail)) or [to_mail, ]
            )
    except:
        if settings.DEBUG:
            raise

def send_email_using_threading(template_name, subject, context=None, recipients=None, sender=settings.EMAIL_FROM, cc=[]):
    t = loader.get_template(template_name)
    body = t.render(Context(context))
    if settings.DEBUG:
        recipients = settings.EMAILS_FOR_DEBUG

    email_msg = EmailMessage(subject=subject, body=body,
                             from_email=sender, to=recipients, bcc=cc)

    email_thread = threading.Thread(target=email_msg.send, args=[True,])
    # This is to tell Python not to wait for the thread to return
    email_thread.setDaemon(True)
    email_thread.start()
