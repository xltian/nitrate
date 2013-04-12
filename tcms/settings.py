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

# Django default settings for tcms project.

import os.path

# Debug settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = False

# Administrators error report email settings

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Database settings

DATABASE_ENGINE = 'mysql'     # 'postgresql_psycopg2', 'postgresql',
                                # 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'nitrate'        # Or path to database file if using sqlite3.
DATABASE_USER = 'adminsTPDLiW'              # Not used with sqlite3.
DATABASE_PASSWORD = 'zgF4ncxBtyjC'          # Not used with sqlite3.
DATABASE_HOST = '127.8.222.1'              # Set to empty string for localhost.
                                # Not used with sqlite3.
DATABASE_PORT = '3306'              # Set to empty string for default.
                                # Not used with sqlite3.

DATABASE_OPTIONS = {}
AUTH_USER_MODEL='auth.User'
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
TESTOPIA_XML_VERSION = '1.0'
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'media').replace('\\','/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# URL prefix for admin absolute URL
ADMIN_PREFIX = '/admin'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't&xaxmguqrfksbmrn3ltt8xcb61k71dzsr6a58k8-^$$!92k_x'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'tcms.core.middleware.CsrfDisableMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.csrf.middleware.CsrfViewMiddleware',
    'django.contrib.csrf.middleware.CsrfResponseMiddleware',
    'tcms.core.lib.django-pagination.pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'tcms.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), '..', 'templates/').replace('\\','/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'kobo.django.xmlrpc',
    'tcms.apps.profiles',
    'tcms.core',
    'tcms.core.contrib.auth',
    'tcms.core.contrib.comments',
    'tcms.core.logs',
    'tcms.apps.management',
    'tcms.apps.testcases',
    'tcms.apps.testplans',
    'tcms.apps.testruns',
    'tcms.apps.testreviews',
    'tcms.core.lib.django-pagination.pagination',

    'tcms.integration.djqpid',
    'tcms.integration.apps.errata',
    'tcms.core.contrib.linkreference',

    'tcms.integration.apps.bugzilla',
)

# RequestContext settings

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'tcms.core.context_processors.admin_prefix_processor',
    'tcms.core.context_processors.admin_media_prefix_processor',
    'tcms.core.context_processors.auth_backend_processor',
    'tcms.core.context_processors.request_contents_processor',
    'tcms.core.context_processors.settings_processor',
)

#
# Default apps settings
#

# Defene the custom comment app
# http://docs.djangoproject.com/en/dev/ref/contrib/comments/custom/

COMMENTS_APP = 'tcms.core.contrib.comments'

# Define the custom profile models
AUTH_PROFILE_MODULE = 'profiles.UserProfile'

#
# XML-RPC interface settings
#
# XML-RPC methods
XMLRPC_METHODS = {
    'TCMS_XML_RPC': (
        ('tcms.xmlrpc.auth', 'Auth'),
        ('tcms.xmlrpc.build', 'Build'),
        ('tcms.xmlrpc.env', 'Env'),
        ('tcms.xmlrpc.product', 'Product'),
        ('tcms.xmlrpc.testcase', 'TestCase'),
        ('tcms.xmlrpc.testcaserun', 'TestCaseRun'),
        ('tcms.xmlrpc.testcaseplan', 'TestCasePlan'),
        ('tcms.xmlrpc.testopia', 'Testopia'),
        ('tcms.xmlrpc.testplan', 'TestPlan'),
        ('tcms.xmlrpc.testrun', 'TestRun'),
        ('tcms.xmlrpc.user', 'User'),
        ('tcms.xmlrpc.version', 'Version'),
        ('tcms.xmlrpc.tag', 'Tag'),
    ),
}

XMLRPC_TEMPLATE = 'xmlrpc.html'

# Cache backend
CACHE_BACKEND = 'locmem://'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# wadofstuff serializer settings
# http://code.google.com/p/wadofstuff/wiki/DjangoFullSerializers
SERIALIZATION_MODULES = {
    'json': 'tcms.core.lib.wadofstuff.django.serializers.json',
}

#
# Debug settings
#
# Debug log file, default is output to console
DEBUG_LOG_FILE = '/tmp/log/shipshape.log'
# Debug level is following:
# - 0 is None
# - 1 is Info
# - 5 is Error
DEBUG_LEVEL = 0

# Needed by django.core.context_processors.debug:
# See http://docs.djangoproject.com/en/dev/ref/templates/api/#django-core-context-processors-debug
INTERNAL_IPS = ('127.8.222.1', )

#
# Plugins
#
SIGNAL_PLUGINS = (
    # 'tcms.plugins.example',
    # 'tcms.plugins.qpid',
)

# Authentication backends
# For the login/register/logout reaon, we only support the internal auth backends.
AUTHENTICATION_BACKENDS = (
    'tcms.core.contrib.auth.backends.DBModelBackend',
)

#
# Mail settings
#
# Set the default send mail address
# See http://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_FROM = 'noreply@foo.com'
EMAIL_SUBJECT_PREFIX = '[TCMS] '

EMAILS_FOR_DEBUG = ['ctang@redhat.com',]

# TCMS email behavior settings
PLAN_EMAIL_TEMPLATE = 'mail/change_plan.txt'
PLAN_DELELE_EMAIL_TEMPLATE = 'mail/delete_plan.txt'
CASE_EMAIL_TEMPLATE = 'mail/edit_case.txt'
CASE_DELETE_EMAIL_TEMPLATE = 'mail/delete_case.txt'

# Maximum upload file size, default set to 5MB.
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_SIZE = 5242880

# Site-specific messages

# The site can supply optional "message of the day" style
# banners, similar to /etc/motd
# They are fragments of HTML.

# This one, if set, is shown on the front page.
# It is only shown to authenticated users
#MOTD_AUTH = """<p>This is a development instance of the TCMS</p>
# <p>(this is MOTD_AUTH)</p>"""

# This one, if set, is shown on the login screen.
# It is shown to unauthenticated users
#MOTD_LOGIN = """<p>This is a development instance of the TCMS</p>
# <p>(this is MOTD_LOGIN)</p>"""

# The URLS will be list in footer
# Example:
#FOOTER_LINKS = (
#   ('mailto:nitrate-dev-list@example.com', 'Contact Us'),
#   ('mailto:nitrate-admin@example.com', 'Request Permission'),
#   ('http://foo.com', 'foo')
#)
FOOTER_LINKS = ()

# Attachement file download path
# it could be spcified to a different out of MEDIA_URL
# FILE_UPLOAD_DIR = path.join(MEDIA_DIR, 'uploads').replace('\\','/'),
FILE_UPLOAD_DIR = '/tmp/uploads'

#
# Installation settings
#
# First run - to detemine need port user or not.
FIRST_RUN = True

# Enable the administrator delete permission
# In another word it's set the admin to super user or not.
SET_ADMIN_AS_SUPERUSER = False

#
# Authentication backend settings
#
# Bugzilla author xmlrpc url
# Required by bugzilla authentication backend
BUGZILLA3_RPC_SERVER = ''
BUGZILLA_URL = ''

# Turn on/off listening signals sent by models.
LISTENING_MODEL_SIGNAL = True

# Kerberos settings
# Required by kerberos authentication backend
KRB5_REALM = ''

# Integration with Errata system, used to linkify the Errata ID
# A valid Errata URL:
ERRATA_URL_PREFIX = 'http://www.redhat.com'
# user guide url:
USER_GUIDE_URL = 'https://www.redhat.com/TCMS-User_Guide/index.html'
