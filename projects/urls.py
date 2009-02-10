from django.conf.urls.defaults import *

from views import list_proposed_projects, list_completed_projects, single_project, add_or_edit_project, add_project, join_project, vote_for_project, search_portal, set_completed_confirm, set_completed_doit, post_project_comment, list_comments, recommended_projects
from tests.data import populate_projects

urlpatterns = patterns('',
		#url(r'^comments/', include('django.contrib.comments.urls')),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/$',
			single_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/postcomment/$',
			post_project_comment),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/join/$',
			join_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/edit/$',
			add_or_edit_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/$',
			set_completed_confirm),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/ok/$',
			set_completed_doit),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/vote/(?P<vote_type>(completed|proposed))/$',
			vote_for_project),
		url(r'^add/$',
			add_project),
		url(r'^completed/(?P<list_type>\w+)/$',
			list_completed_projects),
		url(r'^proposed/(?P<list_type>\w+)/$',
			list_proposed_projects),
		url(r'^comments/$',
			list_comments),
		url(r'^completed/$',
			list_completed_projects),
		url(r'^proposed/$',
			list_proposed_projects),
		url(r'^(?P<completed_or_proposed>(completed|proposed))/recommended/$',
			recommended_projects),
		url(r'^search/$',
			search_portal),
		url(r'^list/$',
			list_proposed_projects),
		url(r'^$',
			list_proposed_projects),
		#url(r'^tag/(?P<tag_name>\w+)/$', 
		#	projects_tagged_with),
	    url(r'^populate/$', 
			populate_projects),
)
