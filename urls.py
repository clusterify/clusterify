from django.conf.urls.defaults import *

from django.contrib import admin
from django.views.generic.simple import direct_to_template

from views import tags_js, hide_announcement

import registration.views

import os.path

admin.autodiscover()

urlpatterns = patterns('',
    #(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),

	(r'^flag/', include('flag.urls')),
	(r'^messages/', include('messages.urls')),
	#(r'^events/', include('eventapp.urls')),
	#(r'^tracking/', include('tracking.urls')),
	

    # Specific views
    #('^$', 'django.views.generic.simple.redirect_to', {'url': '/projects/'}),
    #('^$',  direct_to_template, {'template': 'home.html'}),
    (r'^tags/js/$', tags_js),

    (r'^hide_announcement/$', hide_announcement),

    # # This should only be used in dev environment (there are better ways to serve static files).
    # (r'^files/(?P<path>.*)$', 'django.views.static.serve',
    #     {'document_root': os.path.join(os.path.dirname(__file__), 'files')}),

    # OpenID related
    # (r'^openid/$', 'django_openidconsumer.views.begin'),
    # (r'^openid/complete/$', 'django_openidconsumer.views.complete',
    #     {'on_success': registration.views.openid_login_on_success}),
    # (r'^openid/signout/$', 'django_openidconsumer.views.signout'),
    # (r'^openid/register/$', 'registration.views.register_from_openid'),
)
