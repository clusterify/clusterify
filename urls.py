from django.conf.urls.defaults import *

from django.contrib import admin
from django.views.generic.simple import direct_to_template

from views import tags_js, hide_announcement

import registration.views

import os.path

admin.autodiscover()

urlpatterns = patterns('',

    (r'^accounts/', include('registration.urls')),

	(r'^flag/', include('flag.urls')),
	(r'^messages/', include('messages.urls')),

    (r'^tags/js/$', tags_js),

    (r'^hide_announcement/$', hide_announcement),

)
