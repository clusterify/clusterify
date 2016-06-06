from django.conf.urls import include, url

import projects.views

urlpatterns = [

		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/$', 
			projects.views.single_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/join/$',
			projects.views.join_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/unjoin/$',
			projects.views.unjoin_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/update_role/$',
			projects.views.update_role),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/(?P<joining_username>\w+)/approve/$',
			projects.views.approve_join),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/edit/$',
			projects.views.add_or_edit_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/$',
			projects.views.set_completed_confirm),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/complete/ok/$',
			projects.views.set_completed_doit),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/vote/(?P<vote_type>(completed|proposed))/$',
			projects.views.vote_for_project),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/become_admin/$',
			projects.views.set_project_admin_confirm),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/become_admin/ok/$',
			projects.views.set_project_admin_doit),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/set_wont_complete/$',
			projects.views.set_wont_be_completed_confirm),
		url(r'^ajax/vote/$',
			projects.views.ajax_vote),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/set_wont_complete/ok/$',
			projects.views.set_wont_be_completed_doit),

		# Comments
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/postcomment/$',
			projects.views.post_project_comment),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/editcomment/(?P<comment_pk>\d+)/$',
			projects.views.edit_project_comment),

		# rss -- only available for top/new projects and comments
		url(r'^rss/(?P<completeness>(completed|proposed))/(?P<list_type>(top|new))/$',
			projects.views.list_projects_as_feed),
		url(r'^rss/(?P<completeness>(completed|proposed))/$',
			projects.views.list_projects_as_feed),
		url(r'^rss/comments/$',
			projects.views.list_comments_as_feed),

		# listing projects
		url(r'^completed/(?P<list_type>(top|new))/$',
			projects.views.list_completed_projects),
		url(r'^proposed/(?P<list_type>(top|new))/$',
			projects.views.list_proposed_projects),
		url(r'^(?P<completeness>(completed|proposed))/recommend/$',
			projects.views.recommended_projects),
		url(r'^completed/$',
			projects.views.list_completed_projects),
		url(r'^proposed/$',
			projects.views.list_proposed_projects),
		url(r'^list/$',
			projects.views.list_proposed_projects),
		url(r'^$', projects.views.list_proposed_projects),
	   
		url(r'^search/$',
			projects.views.search_portal),
		url(r'^comments/$',
			projects.views.list_comments),
		url(r'^add/$',
			projects.views.add_project),
]
