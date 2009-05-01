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

import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.utils import feedgenerator
from django.core.mail import send_mail
from django.conf import settings

from tagging.models import TaggedItem

from clusterify.utils import get_paginator_page, generic_confirmation_view, get_query, get_full_url, oops

from registration.models import Profile

from forms import ProjectForm, CommentForm, JoinForm
from models import Project, Comment, Membership
from eventapp.models import Event
##############################################################################
# Constants

PROJECTS_PER_PAGE = 10
ITEMS_IN_FEED = 20
SEEDS_PER_PAGE = 20


##############################################################################
# Project listing & search

# List of projects, filtered by different criterion
def list_projects(request, list_type='top', is_completed=None, return_raw_projects=False):
	user = request.user
	tags = request.GET.get('tags', "")
	for_user = request.GET.get('foruser', "")
	terms = request.GET.get('terms', "")
	
	projects = None
	
	page_title = "Project list"
	filter_description = ""
	
	# Filter by tags (comes first since we use TaggedItem.objects.get_by_model)
	if list_type=='recommend':
		profile = Profile.objects.get(user=user)
		user_tags = profile.get_tags()
		
		# get all projects matching >=1 of the user's tags
		projects = TaggedItem.objects.get_union_by_model(Project, user_tags)
	elif tags != "":
		projects = TaggedItem.objects.get_by_model(Project, tags)
		filter_description += "<li>tags: %s</li>" % tags
	# or select a first crude set of results to be filtered
	else:
		projects = Project.objects.all()
	
	# Filter by completeness
	if not is_completed is None:
		if is_completed:
			page_title = "Completed projects"
			projects = projects.filter(p_completed=True, wont_be_completed=False)
		else:
			page_title = "Proposed projects"
			projects = projects.filter(p_completed=False, wont_be_completed=False)
	
	# Filter by search terms
	if terms != "":
		page_title = "Search results for '%s'" % terms
		query = get_query(terms, ['title', 'description_markdown',])
		projects = projects.filter(query)
	
	# Filter by user
	if for_user != "":
		filter_description += "<li>user: %s</li>" % for_user
		for_user_obj = get_object_or_404(User, username=for_user)
		projects = projects.filter(author=for_user_obj)
	
	# Prepare query string given filters, for link URLs
	qs = ""
	qs_dict = {}
	if tags:
		qs_dict['tags'] = tags
	if for_user:
		qs_dict['foruser'] = for_user
	if terms:
		qs_dict['terms'] = terms
	if qs_dict:
		qs = "?" + urllib.urlencode(qs_dict)
		
	top_url = '/projects/' + (is_completed and 'completed' or 'proposed') + '/top/' + qs
	new_url = '/projects/' + (is_completed and 'completed' or 'proposed') + '/new/' + qs
	mytags_url = '/projects/' + (is_completed and 'completed' or 'proposed') + '/recommend/' + qs
	this_page_url = None
	
	# Order results
	page_url = ""
	rss_url = ""
	if list_type == 'new':
		this_page_url = new_url
		rss_url = '/projects/rss/' + (is_completed and 'completed' or 'proposed') + '/new/' + qs
		projects = projects.order_by('-pub_date')
	elif list_type == 'recommend':
		this_page_url = mytags_url
	else:
		rss_url = '/projects/rss/' + (is_completed and 'completed' or 'proposed') + '/top/' + qs
		this_page_url = top_url
		if is_completed:
			projects = projects.order_by('-score_completed')
		else:
			projects = projects.order_by('-score_proposed')
	
	# For RSS feeds
	if return_raw_projects:
		return page_title, this_page_url, projects, list_type
	
	list_paginator_page = get_paginator_page(request, projects, PROJECTS_PER_PAGE)
	
	return render_to_response('projects/project_list.html',
			{'project_list_page':list_paginator_page,
			'page_title': page_title,
            'list_type': list_type,
			'filter_description': filter_description,
			# TODO: also include tags in those urls
			'list_top_url': top_url,
			'list_new_url': new_url,
			'search_results_type':terms and 'projects' or '',
			'search_terms':terms and terms or '',
			'rss_url': rss_url,
			'list_mytags_url': mytags_url},
			context_instance=RequestContext(request))

def list_projects_as_feed(request, completeness, list_type='top'):
	page_title, url, projects, list_type = list_projects(request, list_type, completeness=='completed', return_raw_projects=True)
	
	f = feedgenerator.Rss201rev2Feed(
			title=page_title + " ("+list_type+")",
			link=get_full_url()+url,
			description=u"",
			language=u"en")

	to_print = projects[0:min(ITEMS_IN_FEED, projects.count())]
	for p in to_print:
		f.add_item(title=p.title, 
				link=get_full_url()+p.get_absolute_url(),
				description=p.description_html,
				pubdate=p.pub_date)
	
	return HttpResponse(f.writeString('UTF-8'), mimetype="application/rss+xml")

def list_comments_as_feed(request):
	page_title, comments = list_comments(request, return_raw_comments=True)

	f = feedgenerator.Rss201rev2Feed(
			title=page_title,
			link=get_full_url(),
			description=u"Recent Project Comments",
			language=u"en")

	to_print = comments[0:min(ITEMS_IN_FEED, comments.count())]
	for p in to_print:
		f.add_item(title="Comment on "+p.project.title+" by "+p.author.username,
				link=get_full_url()+p.project.get_absolute_url(),
				description=p.text,
				pubdate=p.pub_date)

	return HttpResponse(f.writeString('UTF-8'), mimetype="application/rss+xml")


@login_required
def recommended_projects(request, completeness):
	return list_projects(request, 'recommend', completeness=='completed')

def list_proposed_projects(request, list_type='top'):
	return list_projects(request, list_type, False)

def list_completed_projects(request, list_type='top'):
	return list_projects(request, list_type, True)

# Redirects to right view based on search result type
def search_portal(request):
	res_type = request.GET.get('search_results_type', '')
	terms = request.GET.get('terms', '')
	
	if res_type == 'profiles':
		return HttpResponseRedirect('/accounts/people/?terms='+terms)
	elif res_type == 'comments':
		return list_comments(request)
	else:
		return list_projects(request)

def project_notification(project, notification_source_user, subject, content, just_to_author=False):
	if just_to_author:
		project_members = [project.author]
	else:
		project_members = [u for u in project.get_joined_users()]
	
	for m in project_members:
		if m != notification_source_user:
			send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,
				[m.email], fail_silently=True)


##############################################################################
# Displays a single project

def single_project(request, project_author, project_pk, comment_form=CommentForm()):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	# Data we can't get through template accessor mechanisms
	similar_projects = TaggedItem.objects.get_related(project, Project, 3)
	
	voted_for_proposed = False
	voted_for_completed = False
	if user.is_authenticated():
		voted_for_proposed = project.user_voted_proposed(user)
		voted_for_completed = project.user_voted_completed(user)
	
	join_status = project.join_status(user)
	
	if join_status != "None":
		role = project.member_role(user)
		join_form = JoinForm(initial={'role':role})
	else:
		join_form = JoinForm()

	return render_to_response('projects/project.html', 
					{'project':project,
					'similar_projects':similar_projects,
					'user_project_status':join_status,
					'join_form':join_form,
					'form':comment_form,
					'voted_for_proposed':voted_for_proposed,
					'voted_for_completed':voted_for_completed},
					context_instance=RequestContext(request))

##############################################################################
# Comment-related

@login_required
def post_project_comment(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)

	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
		        text = comment_form.cleaned_data['text']
			comment = Comment(text=text, author=user, project=project)
			comment.save()
			
			project_notification(project, user, "Clusterify -- new comment on project",
						render_to_string('projects/emails/comment_on_project.txt',
										{ 'project': project,
										'comment': comment,
										'site_url': get_full_url()}))
			
			return HttpResponseRedirect(project.get_absolute_url())
	else:
		comment_form = CommentForm()
		
	return single_project(request, project_author, project_pk, comment_form)
	
@login_required
def edit_project_comment(request, project_author, project_pk, comment_pk):
	user = request.user
	comment = get_object_or_404(Comment, pk=comment_pk)
	
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		
		if comment_form.is_valid():
			comment.text = comment_form.cleaned_data['text']
			comment.save()
			
			return HttpResponseRedirect(comment.get_edit_url())
	else:
		comment_form = CommentForm(initial={'text':comment.text})
		
	return render_to_response('projects/edit_comment.html',
							{'comment':comment,
							'form':comment_form},
							context_instance=RequestContext(request))

def list_comments(request, return_raw_comments=False):
	terms = request.GET.get('terms', '')
	for_user = request.GET.get('foruser', '')
	
	page_title = "Latest comments on projects"
	filter_description = ""
	use_filter_description = False
	
	comments = Comment.objects.all().order_by("-pub_date")

	# For RSS feeds
	if return_raw_comments:
		return page_title, comments

	if for_user:
		for_user_obj = get_object_or_404(User, username=for_user)
		
		filter_description += "<li>user: %s</li>" % for_user
		page_title = "Latest comments for user '%s'" % for_user
		
		comments = comments.filter(author=for_user_obj)
	
	if terms:
		page_title = "Searching latest comments for '%s'" % terms
		use_filter_description = True
		query = get_query(terms, ['text',])
		comments = comments.filter(query)
	
	comments = comments.order_by('-pub_date')
	
	paginated_comments = get_paginator_page(request, comments, PROJECTS_PER_PAGE)
	
	return render_to_response('projects/comment_list.html',
			{'page_title': page_title,
			'filter_description': use_filter_description and filter_description or None,
			'search_results_type':terms and 'comments' or '',
			'search_terms':terms and terms or '',
			'paginated_comments': paginated_comments},
			context_instance=RequestContext(request))

##############################################################################
# Add/edit projects

@login_required
def add_project(request):
	return add_or_edit_project(request, is_add=True)

@login_required
def add_or_edit_project(request, project_author=None, project_pk=None, is_add=False):
	user = request.user
	
	project = None
	if not is_add:
		project = get_object_or_404(Project, pk=project_pk)
		
		if project.wont_be_completed:
			return oops("This project is set as 'won't be completed': you can't edit it")

		# only a project's author can edit it
		if(not user == project.author):
			return oops("Only a project's author can edit it.")
		

	if request.method == 'POST':
		if is_add:
			project = Project(proposed_by=user, author=user)
		elif project.author != user:
			return oops("Only a project's author can edit it.")
		
		form = ProjectForm(request.POST)
		if form.is_valid():
			project.title = form.cleaned_data['title']
			if form.cleaned_data['event']:
				project.event = get_object_or_404(Event, pk=form.cleaned_data['event'])
			project.description_markdown = form.cleaned_data['description']
			if form.cleaned_data['time_estimate']:
				project.hour_estimate = form.cleaned_data['time_estimate']
			if project.p_completed:
				project.showcase_markdown = form.cleaned_data['showcase']
			
			if not project.p_completed:
				not_involved = form.cleaned_data['not_involved']
				if not_involved:
					project.looking_for_admin = True
					if not is_add:
						user.message_set.create(message="The project is now set as 'looking for admin'. You have admin rights until someone else clicks 'Become admin for this project'.")
						project.remove_member(user)
				else:
					project.looking_for_admin = False
			
			tags = form.cleaned_data['tags']

			project.save()
			
			# Need to save() before calling this, so we couldn't do it up there
			if is_add and not not_involved:
				project.join_user(user)
			
			project.set_tags(tags)

			
			return HttpResponseRedirect(project.get_absolute_url())
	elif not is_add:
		# initialize the form with existing project info
		form = ProjectForm(initial={
						'title':project.title,
						'description':project.description_markdown,
						'showcase':project.showcase_markdown,
						'tags':project.get_editable_tags,
						'time_estimate':project.hour_estimate})
	else:
		form = ProjectForm()

	return render_to_response('projects/add_or_edit_project.html',
		{'form': form,
		'is_editing': not is_add,
		'project': project},
		context_instance=RequestContext(request))

##############################################################################
# Settings various simpler one-at-a-time properties of projects

@login_required
def set_project_admin_confirm(request, project_author, project_pk):
	project = get_object_or_404(Project, pk=project_pk)
	
	if not project.looking_for_admin:
		return oops("")
			   
	if project.wont_be_completed:
		return oops("The project is set as 'won't be completed': you can't do that.")
			   
	return generic_confirmation_view(request,
			"Are you sure you want to become admin for this project?",
			project.get_absolute_url() + "become_admin/ok/",
			project.get_absolute_url())

@login_required
def set_project_admin_doit(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	if not project.looking_for_admin:
		return oops("")
			   
	if project.wont_be_completed:
		return oops("The project is set as 'won't be completed': you can't do that.")
	
	project.author = user
	project.join_user(user)
	project.looking_for_admin = False
	project.save()
	
	# TODO: post notification of admin change
	
	user.message_set.create(message="You are now admin for this project.")
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def set_completed_confirm(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	# only a project's author can edit it
	if not user == project.author:
		return oops("")
			   
	if project.wont_be_completed:
		return oops("The project is set as 'won't be completed': you can't do that.")
	
	return generic_confirmation_view(request,
			"Are you sure you want to set the project as completed?",
			"ok/",
			project.get_absolute_url())

@login_required
def set_completed_doit(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)

	# only a project's author can edit it
	if(not user == project.author):
		return oops("")
			   
	if project.wont_be_completed:
		return oops("The project is set as 'won't be completed': you can't do that.")

	project.p_completed = True
	project.looking_for_admin = False
	project.save()
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def set_wont_be_completed_confirm(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	# only a project's author can edit it
	if not user == project.author:
		return oops("")
	
	return generic_confirmation_view(request,
			"Are you sure you want to set this project as 'won't be completed'. This will remove the project from the 'proposed' lists without putting it on the 'completed' list.",
			"ok/",
			project.get_absolute_url())

@login_required
def set_wont_be_completed_doit(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)

	# only a project's author can edit it
	if not user == project.author and not project.p_completed:
		return render_to_response('oops.html', {},
		       context_instance=RequestContext(request))
			   
	if project.wont_be_completed:
		return oops("The project is already set as 'won't be completed': you can't do that.")

	project.wont_be_completed = True
	project.looking_for_admin = False # no point anymore
	project.save()
	
	project_notification(project, user, "Clusterify -- project has been set as 'won't be completed'",
				render_to_string('projects/emails/project_wont_be_completed.txt',
								{ 'project': project,
								'site_url': get_full_url()}))
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def join_project(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	if project.wont_be_completed:
		return oops("This project won't be completed: you can't join it.")
	
	if request.method == 'POST':
		form = JoinForm(request.POST)
		role = form.cleaned_data['role']
		if form.is_valid():
			project.add_interested_user(user, role)
		
			project_notification(project, user, "Clusterify -- user wants to join project",
					render_to_string('projects/emails/author_approve_join.txt',
									{ 'project': project,
									'role': role,
									'joining_user': user,
									'site_url': get_full_url()}), True)
		else:
			user.message_set.create(message="Something was wrong with your form. Please note that your role description may not be longer than 120 characters. " % role)

	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def unjoin_project(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	project.remove_member(user)
	user.message_set.create(message="You have been removed from this project")
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def update_role(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	membership = get_object_or_404(Membership, project=project, user=user)
	
	if request.method == 'POST':
		form = JoinForm(request.POST)
		
		if form.is_valid():
			role = form.cleaned_data['role']
			
			membership.role = role
			membership.save()
		else:
			user.message_set.create(message="Something was wrong with your form. Please note that your role description may not be longer than 120 characters. Here's the text you entered: %s" % role)
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def approve_join(request, project_author, project_pk, joining_username):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	joining_user = get_object_or_404(User, username=joining_username)
	
	if(user == project.author):
		project.join_user(joining_user)
		
		role = project.member_role(joining_user)
		
		project_notification(project, None, "Clusterify -- new user joined project",
			render_to_string('projects/emails/join_approved.txt',
							{ 'project': project,
							'role': role,
							'joining_user': joining_user,
							'site_url': get_full_url()}))
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def vote_for_project(request, project_author, project_pk, vote_type):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	try:
		if vote_type == 'completed':
			project.add_completed_vote(user)
		else:
			project.add_proposed_vote(user)
	except:
		user.message_set.create(message="You have already voted for this item.")
	
	return HttpResponseRedirect(project.get_absolute_url())

	
@login_required
def ajax_vote(request):
	project = Project.objects.get(pk=int(request.POST['project'][7:]))#slicing for stripping the "project" prefix
	try: 
		return HttpResponse(project.add_proposed_vote(request.user))
	except Exception, e:
		return HttpResponseServerError(e.message)
        
