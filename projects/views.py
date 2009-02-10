import datetime
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext

from tagging.models import Tag, TaggedItem

from progjects.utils import get_paginator_page, generic_confirmation_view, get_query

from registration.models import Profile

from forms import ProjectForm, CommentForm
from models import Project, Comment

PROJECTS_PER_PAGE = 10



##############################################################################
# Project listing & search

# List of projects, filtered by different criterion
def list_projects(request, list_type='top', is_completed=None):
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
	if tags != "":
		projects = TaggedItem.objects.get_by_model(Project, tags)
		filter_description += "<li>tags: %s</li>" % tags
	# or select a first crude set of results to be filtered
	else:
		projects = Project.objects.all()
	
	# Filter by completeness
	if not is_completed is None:
		if is_completed:
			page_title = "Completed project list"
			projects = projects.filter(p_completed=True)
		else:
			page_title = "Proposed project list"
			projects = projects.filter(p_completed=False)
	
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
	
	# Order results
	if list_type == 'new':
		page_title += " (new)"
		projects = projects.order_by('-pub_date')
	elif list_type == 'recommend':
		page_title += " (my tags)"
	else:
		page_title += " (top)"
		if is_completed:
			projects = projects.order_by('-score_completed')
		else:
			projects = projects.order_by('-score_proposed')
	
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
	
	# ...
	list_paginator_page = get_paginator_page(request, projects, PROJECTS_PER_PAGE)
	
	return render_to_response('projects/project_list.html',
			{'project_list_page':list_paginator_page,
			'page_title': page_title,
			'filter_description': filter_description,
			# TODO: also include tags in those urls
			'list_top_url': '/projects/' + (is_completed and 'completed' or 'proposed') + '/top/' + qs,
			'list_new_url': '/projects/' + (is_completed and 'completed' or 'proposed') + '/new/' + qs,
			'list_mytags_url': '/projects/' + (is_completed and 'completed' or 'proposed') + '/recommend/' + qs},
			context_instance=RequestContext(request))

@login_required
def recommended_projects(request, completed_or_proposed):
	return list_projects(request, 'recommend', completed_or_proposed=='completed')

def list_proposed_projects(request, list_type='top'):
	return list_projects(request, list_type, False)

def list_completed_projects(request, list_type='top'):
	return list_projects(request, list_type, True)

# Redirects to right view based on search result type
def search_portal(request):
	res_type = request.GET.get('search_results_type', '')
	terms = request.GET.get('terms', '')
	
	if res_type == 'profiles':
		return HttpResponseRedirect('/accounts/profile/search/?terms='+terms)
	elif res_type == 'comments':
		return list_comments(request)
	else:
		return list_projects(request)

##############################################################################
# Displays a single project

def single_project(request, project_author, project_pk, comment_form=CommentForm()):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	# Data we can't get through template accessor mechanisms
	similar_projects = TaggedItem.objects.get_related(project, Project, 3)
	
	user_not_in_project = True
	if project.join_status(user) != "None":
		user_not_in_project = False
	
	voted_for_proposed = False
	voted_for_completed = False
	if user.is_authenticated():
		voted_for_proposed = project.user_voted_proposed(user)
		voted_for_completed = project.user_voted_completed(user)
	
	return render_to_response('projects/project.html', 
					{'project':project,
					'similar_projects':similar_projects,
					'user_not_in_project':user_not_in_project,
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
			
			return HttpResponseRedirect(project.get_absolute_url())
	else:
		comment_form = CommentForm()
		
	return single_project(request, project_author, project_pk, comment_form)

def list_comments(request):
	terms = request.GET.get('terms', '')
	for_user = request.GET.get('foruser', '')
	
	page_title = "Latest comments on projects"
	filter_description = ""
	use_filter_description = False
	
	comments = Comment.objects.all()
	
	if for_user:
		for_user_obj = get_object_or_404(User, username=for_user)
		
		filter_description += "<li>user: %s</li>" % for_user
		page_title = "Latest comments for user '%s'" % for_user
		
		comments = comments.filter(author=for_user_obj)
	
	if terms:
		page_title = "Searching latest comments for '%s'" % terms
		use_filter_description = True
		query = get_query(terms, ['text',])
		projects = comments.filter(query)
	
	comments = comments.order_by('-pub_date')
	
	paginated_comments = get_paginator_page(request, comments, PROJECTS_PER_PAGE)
	
	return render_to_response('projects/comment_list.html',
			{'page_title': page_title,
			'filter_description': use_filter_description and filter_description or None,
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
	
	# TODO: make sure user == project.author
	if request.method == 'POST':
		if is_add:
			project = Project(author=user)
		
		form = ProjectForm(request.POST)
		if form.is_valid():
			project.title = form.cleaned_data['title']
			project.description_markdown = form.cleaned_data['description']
			if form.cleaned_data['time_estimate']:
				project.hour_estimate = form.cleaned_data['time_estimate']
			
			required_tags = form.cleaned_data['required_tags']
			description_tags = form.cleaned_data['description_tags']
			
			project.save()

			project.set_description_tags(description_tags)
			project.set_required_tags(required_tags)
			
			return HttpResponseRedirect(project.get_absolute_url())
	elif not is_add:
		#convert list of Tags to string for editing
		editable_desc_tags = project.get_editable_desc_tags()
		editable_reqd_tags = project.get_editable_reqd_tags()

		# initialize the form with existing project info
		form = ProjectForm(initial={
						'title':project.title,
						'description':project.description_markdown,
						'description_tags':editable_desc_tags,
						'required_tags':editable_reqd_tags,
						'time_estimate':project.hour_estimate})
	else:
		form = ProjectForm()

	return render_to_response('projects/add_or_edit_project.html',
		{'form': form,
		'is_editing': not is_add},
		context_instance=RequestContext(request))

##############################################################################
# Settings various simpler one-at-a-time properties of projects

@login_required
def set_completed_confirm(request, project_author, project_pk):
	project = get_object_or_404(Project, pk=project_pk)
	
	# TODO: verify the user is the author
	
	return generic_confirmation_view(request,
			"Are you sure you want to set the project as completed?",
			"ok/",
			project.get_absolute_url())

@login_required
def set_completed_doit(request, project_author, project_pk):
	project = get_object_or_404(Project, pk=project_pk)
	
	# TODO: verify the user is the author
	project.p_completed = True
	project.save()
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def join_project(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	project.join_user(user)
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def vote_for_project(request, project_author, project_pk, vote_type):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	if vote_type == 'completed':
		project.add_completed_vote(user)
	else:
		project.add_proposed_vote(user)
	
	return HttpResponseRedirect(project.get_absolute_url())
