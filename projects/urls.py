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

urlpatterns = patterns('projects.views',
		
		# Individual project actions
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/$',
			'single_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/join/$',
			'join_project'),
		url(r'^list/(?P<project_author>\w+)/(?P<project_pk>\d+)/unjoin/$',
			'unjoin_project'),
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
	   
		url(r'^search/$',
			'search_portal'),
		url(r'^comments/$',
			'list_comments'),
		url(r'^add/$',
			'add_project'),
)
