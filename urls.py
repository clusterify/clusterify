from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template

from views import tags_js

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^clusterify/', include('clusterify.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/', include('registration.urls')),
    (r'^projects/', include('projects.urls')),
    (r'^tags/js/$', tags_js),
	(r'^concepts/$', direct_to_template, {'template': 'concepts.html'}),
    # TODO: remove this in prod
    (r'^files/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'files')}),
    ('^$', 'django.views.generic.simple.redirect_to', {'url': '/projects/'}),
)
