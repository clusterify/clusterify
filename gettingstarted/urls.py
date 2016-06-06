from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import hello.views

from django.views.generic import TemplateView
urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^projects/', include('projects.urls')),
    ##url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='registration/profile.html')),
	
	url(r'^$', TemplateView.as_view(template_name='homepage.html'), name="home"),

    url(r'^concepts/$', TemplateView.as_view(template_name='concepts.html')),
    url(r'^about/$', TemplateView.as_view(template_name='about.html')),
    url(r'^terms/$', TemplateView.as_view(template_name='terms.html')),
    url(r'^collaboration/$', TemplateView.as_view(template_name='collaboration.html')),
    url(r'^idea_guide/$', TemplateView.as_view(template_name='idea_guide.html')),

]
