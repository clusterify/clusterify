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

from django.conf.urls.defaults import *

from django.contrib import admin
from django.views.generic.simple import direct_to_template

from views import tags_js, hide_announcement

import registration.views

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/', include('registration.urls')),
    (r'^projects/', include('projects.urls')),
	(r'^flag/', include('flag.urls')),
	(r'^messages/', include('messages.urls')),
	

    # Specific views
    ('^$', 'django.views.generic.simple.redirect_to', {'url': '/projects/'}),
    (r'^tags/js/$', tags_js),
    (r'^concepts/$', direct_to_template, {'template': 'concepts.html'}),
    (r'^about/$', direct_to_template, {'template': 'about.html'}),
    (r'^terms/$', direct_to_template, {'template': 'terms.html'}),
    (r'^collaboration/$', direct_to_template, {'template': 'collaboration.html'}),
    (r'^idea_guide/$', direct_to_template, {'template': 'idea_guide.html'}),
    (r'^hide_announcement/$', hide_announcement),

    # This should only be used in dev environment (there are better ways to serve static files).
    (r'^files/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'files')}),

    # OpenID related
    (r'^openid/$', 'django_openidconsumer.views.begin'),
    (r'^openid/complete/$', 'django_openidconsumer.views.complete',
        {'on_success': registration.views.openid_login_on_success}),
    (r'^openid/signout/$', 'django_openidconsumer.views.signout'),
    (r'^openid/register/$', 'registration.views.register_from_openid'),
)
