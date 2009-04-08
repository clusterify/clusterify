"""
"The contents of this file are subject to the Common Public Attribution
License Version 1.0 (the "License"); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at 
http://www.clusterify.com/files/CODE_LICENSE.txt. The License is based 
on the Mozilla Public License Version 1.1 but Sections 14 and 15 have 
been added to cover use of software over a computer network and provide 
for limited attribution for the Original Developer. In addition, Exhibit 
A has been modified to be consistent with Exhibit B.

Software distributed under the License is distributed on an "AS IS" basis, 
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
for the specific language governing rights and limitations under the 
License.

The Original Code is Clusterify.

The Initial Developer of the Original Code is "the Clusterify.com team", 
which is described at http://www.clusterify.com/about/. All portions of 
the code written by the Initial Developer are Copyright (c) the Initial 
Developer. All Rights Reserved.
"""

# Django settings for clusterify project.

import os.path

import settings_not_in_svn

PROJECT_DIR = os.path.join(os.path.dirname(__file__),"..")

DEBUG = False 
TEMPLATE_DEBUG = DEBUG

# This is used on error pages
DEFAULT_CONTACT_EMAIL = 'webmaster@clusterify.com'

ADMINS = (
    ('ClusterifyAdmins', 'webmaster@clusterify.com'),
)

# This is to allow sessions to work both on www.clutsterify.com and just clusterify.com
SESSION_COOKIE_DOMAIN = 'clusterify.com'

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'mediapostgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = settings_not_in_svn.DATABASE_NAME             # Or path to database file if using sqlite3.
DATABASE_USER = settings_not_in_svn.DATABASE_USER             # Not used with sqlite3.
DATABASE_PASSWORD = settings_not_in_svn.DATABASE_PASSWORD         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Montreal'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.clusterify.com/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = settings_not_in_svn.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)


TEMPLATE_CONTEXT_PROCESSORS = (
	# to make User available to the Templates
	'django.core.context_processors.auth',
	'clusterify.views.should_hide_announcement',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openidconsumer.middleware.OpenIDMiddleware',
)

ROOT_URLCONF = 'clusterify.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.admin',
    'registration',
    'projects',
    'tagging',
    'voting',
    'django_openidconsumer',
    'django_evolution',
)

# for registration
DEFAULT_FROM_EMAIL=settings_not_in_svn.DEFAULT_FROM_EMAIL
ACCOUNT_ACTIVATION_DAYS=7
EMAIL_HOST=settings_not_in_svn.EMAIL_HOST
EMAIL_PORT=settings_not_in_svn.EMAIL_PORT
EMAIL_HOST_USER=settings_not_in_svn.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=settings_not_in_svn.EMAIL_HOST_PASSWORD
SERVER_EMAIL=settings_not_in_svn.SERVER_EMAIL

# to do user.get_profile
AUTH_PROFILE_MODULE = 'registration.Profile'

# added for openid support
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend','registration.models.OpenIdBackend',)
