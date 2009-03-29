from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
		url(r'^add/$',
			'add_project'),
		
		# Individual project actions
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/$',
			'single_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/join/$',
			'join_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/update_role/$',
			'update_role'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/(?P<joining_username>\w+)/approve/$',
			'approve_join'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/edit/$',
			'add_or_edit_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/$',
			'set_completed_confirm'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/ok/$',
			'set_completed_doit'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/vote/(?P<vote_type>(completed|proposed))/$',
			'vote_for_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/become_admin/$',
			'set_project_admin_confirm'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/become_admin/ok/$',
			'set_project_admin_doit'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/set_wont_complete/$',
			'set_wont_be_completed_confirm'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/set_wont_complete/ok/$',
			'set_wont_be_completed_doit'),

		# Comments
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/postcomment/$',
			'post_project_comment'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/editcomment/(?P<comment_pk>\d+)/$',
			'edit_project_comment'),
		url(r'^comments/$',
			'list_comments'),

		# rss -- only available for top/new projects and comments
		url(r'^rss/(?P<completeness>(completed|proposed))/(?P<list_type>(top|new))/$',
			'list_projects_as_feed'),
		url(r'^rss/(?P<completeness>(completed|proposed))/$',
			'list_projects_as_feed'),
		url(r'^rss/comments/$',
			'list_comments_as_feed'),

		# listing projects
		url(r'^completed/(?P<list_type>(top|new))/$',
			'list_completed_projects'),
		url(r'^proposed/(?P<list_type>(top|new))/$',
			'list_proposed_projects'),
		url(r'^(?P<completeness>(completed|proposed))/recommend/$',
			'recommended_projects'),
		url(r'^completed/$',
			'list_completed_projects'),
		url(r'^proposed/$',
			'list_proposed_projects'),
		url(r'^list/$',
			'list_proposed_projects'),
		url(r'^$',
			'list_proposed_projects'),
	   
		# ...
		url(r'^search/$',
			'search_portal'),
)
