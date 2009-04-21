"""
URLConf for Django user registration and authentication.

If the default behavior of the registration views is acceptable to
you, simply use a line like this in your root URLConf to set up the
default URLs for registration::

    (r'^accounts/', include('registration.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

But if you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead. If you do, it's a
good idea to use the names ``registration_activate``,
``registration_complete`` and ``registration_register`` for the
various steps of the user-signup process.

"""


from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_reset, password_reset_done, password_change, password_change_done

from registration.views import activate, register, edit_profile, view_profile, view_default_profile, view_comments, view_projects, list_users, list_users_as_feed, list_users_mytags, logout


urlpatterns = patterns('',
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           name='registration_activate'),
                       url(r'^login/$',
                           auth_views.login,
                           {'template_name': 'registration/login.html'},
                           name='auth_login'),
                       url(r'^logout/$',
                           logout,
                           name='logout'),
                       #url(r'^password/change/$',
                       #    auth_views.password_change,
                       #    name='auth_password_change'),
                       #url(r'^password/change/done/$',
                       #    auth_views.password_change_done,
                       #    name='auth_password_change_done'),
                       #url(r'^password/reset/$',
                       #    auth_views.password_reset,
                       #    name='auth_password_reset'),
                       #url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                       #    auth_views.password_reset_confirm,
                       #    name='auth_password_reset_confirm'),
                       #url(r'^password/reset/complete/$',
                       #    auth_views.password_reset_complete,
                       #    name='auth_password_reset_complete'),
                       #url(r'^password/reset/done/$',
                       #    auth_views.password_reset_done,
                       #    name='auth_password_reset_done'),
                       url(r'^register/$',
                           register,
                           name='registration_register'),
                       url(r'^register/complete/$',
                           direct_to_template,
                           {'template': 'registration/registration_complete.html'},
                           name='registration_complete'),
                       # MODIF: added these two handlers
                       url(r'^profile/edit/$',
                          edit_profile),
                       url(r'^people/recommend/$',
                          list_users_mytags),
                       # Important that /recommend/ comes first, as we need @login_required for that list_type
                       url(r'^people/(?P<list_type>\w+)/$',
                          list_users),
                       url(r'^people/$',
                          list_users),
                       url(r'^profile/view/(?P<username>\w+)/$',
                          view_profile),
                       # rss
                       url(r'^rss/(?P<list_type>(top|new))/$',
                          list_users_as_feed),
                       #url(r'^profile/view/(?P<username>\w+)/comments/$',
                       #   view_comments),
                       #url(r'^profile/view/(?P<username>\w+)/projects/$',
                       #   view_projects),
                       url(r'^profile/$',
                          view_default_profile),
     )

urlpatterns += patterns('',
  (r'^password/reset/$', password_reset,
  	{'template_name': 'registration/password_reset.html',
	'email_template_name':'registration/password_reset_email.html',
	'post_reset_redirect': '/accounts/password/reset/email_sent/'}),
  (r'^password/reset/email_sent/$', password_reset_done,
  	{'template_name': 'registration/password_reset_done.html'}),
  (r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
  	'django.contrib.auth.views.password_reset_confirm',
	{'template_name':'registration/password_reset_confirm.html',
	'post_reset_redirect': '/accounts/password/reset/complete/'}),
  (r'^password/reset/complete/$',
  	'django.contrib.auth.views.password_reset_complete',
  	{'template_name':'registration/password_reset_complete.html'}),

  (r'^password/change/$', password_change,
  	{'template_name': 'registration/password_change.html',
	'post_change_redirect': '/accounts/password/change/done'}),
  (r'^password/change/done/$', password_change_done,
  	{'template_name': 'registration/password_change_done.html'}),
)
