#!/usr/bin/python
# encoding: utf-8

import os
import urllib2
import socket
from sgmllib import SGMLParser
from django.core.mail import send_mail
from pprint import pprint

# =========================================
# Settings
# =========================================

TCMS_SETTINGS = 'tcms.product_settings'

ADMINS = (
    ('Xuqing Kuang', 'xkuang@redhat.com'),
    ('Victor Chen', 'vchen@redhat.com'),
)

PRODUCTS_CONFIG = (
    ('Red Hat Enterprise Linux 6', 'RHEL6.0-', 'http://www.redhat.com/'),
)

HOST_NAME = socket.gethostname()

MAIL_SUBJECT = '[TCMS] New builds has been synced from the tree - %s' % HOST_NAME
MAIL_FROM = 'noreply@redhat.com'
MAIL_HEADER = 'Following new builds has been synced from the tree:\n\n- %s -\n\n' % HOST_NAME

# =========================================
# Code starting
# =========================================

os.environ['DJANGO_SETTINGS_MODULE'] = TCMS_SETTINGS

from tcms.apps.management.models import Product, TestBuild

class URLListName(SGMLParser):
    """Strip all of a tag from html"""
    is_a=""
    name=[]
    def start_a(self, attrs):
        self.is_a=1
    def end_a(self):
        self.is_a=""
    def handle_data(self, text):
        if self.is_a:
            self.name.append(text)

class BuildSync(object):
    """Sync the builds from HTMLs"""
    def __init__(self, product_config):
        """Initial the data"""
        self.link_list = None
        self.builds_list = {}
        self.create_builds_list = []
        self.product_config = product_config

    def open_url(self, url):
        """Open the URLs from settings and save the links"""
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        opener = urllib2.build_opener()
        data = opener.open(request).read()

        url_list = URLListName()
        url_list.feed(data)
        self.link_list = url_list.name

    def process_builds(self):
        """Process the builds to a dictionary"""
        for p in self.product_config:
            p_str = p[0]

            for l in self.link_list:
                if l.startswith(p[1]):
                    if not self.builds_list.has_key(p_str):
                        self.builds_list[p_str] = []
                    b_str = l.replace('/', '')
                    self.builds_list[p_str].append(b_str)

    def create_builds(self):
        """Create the database instance of builds"""
        ps = Product.objects.filter(name__in = self.builds_list.keys())

        # Create the builds
        for p in ps:
            for p_str, b_list in self.builds_list.items():
                if p.name == p_str:
                    for b_str in b_list:
                        b, c = TestBuild.objects.get_or_create(
                            name = b_str,
                            product = p,
                        )

                        if c:
                            self.create_builds_list.append(b.pk)

    def send_notification(self):
        """Sending the notificaton to the ADMIN in settings"""
        # Sending the notification
        tbs = TestBuild.objects.filter(pk__in = self.create_builds_list)
        tbs = tbs.order_by('product')

        tbp_pks = list(set(tbs.values_list('product', flat=True)))
        ps = Product.objects.filter(pk__in = tbp_pks)

        message = MAIL_HEADER

        line = '=' * 30 + '\n'

        for p in ps:
            p_str = unicode(p)

            message += line + p_str + '\n' + line
            for tb in tbs:
                if tb.product == p:
                    message += '* ' + unicode(tb) + '\n'
            message += '\n'

        mail_to = []
        for admin in ADMINS:
            mail_to.append(admin[1])

        send_mail(MAIL_SUBJECT, message, MAIL_FROM, mail_to)

    def run(self):
        """Start the program"""
        for pc in self.product_config:
            self.open_url(pc[2])
            self.process_builds()

        self.create_builds()

        if self.create_builds_list and ADMINS:
            self.send_notification()

if __name__ == '__main__':
    build_sync = BuildSync(product_config = PRODUCTS_CONFIG)
    build_sync.run()
