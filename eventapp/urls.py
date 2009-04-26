from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'eventapp.views.list_upcoming_events', name='eventapp_upcoming_events'),
    url(r'^upcoming/$', 'eventapp.views.list_upcoming_events', name='eventapp_upcoming_events'),
    url(r'^past/$', 'eventapp.views.list_past_events', name='eventapp_past_events'),    
    url(r'^add/$', 'eventapp.views.add_event'),
    url(r'(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 'eventapp.views.single_event', name='eventapp_view_event'),
    url(r'^edit/(?P<event_pk>[-\w]+)/$', 'eventapp.views.add_or_edit_event', name='add_or_edit_event'),
    url(r'^comment/(?P<event_pk>[-\w]+)/$', 'eventapp.views.post_event_comment', name='post_event_comment'),
    url(r'^editcomment/(?P<comment_pk>[-\w]+)/$', 'eventapp.views.edit_event_comment', name='edit_event_comment'),
)
