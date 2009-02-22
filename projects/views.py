import datetime
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.utils import feedgenerator
from django.core.mail import send_mail
from django.conf import settings

from tagging.models import Tag, TaggedItem

from clusterify.utils import get_paginator_page, generic_confirmation_view, get_query

from registration.models import Profile

from forms import ProjectForm, CommentForm, SeedForm
from models import Project, Comment, Seed

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
		page_title += " (new)"
		this_page_url = new_url
		rss_url = '/projects/rss/' + (is_completed and 'completed' or 'proposed') + '/new/' + qs
		projects = projects.order_by('-pub_date')
	elif list_type == 'recommend':
		page_title += " (my tags)"
		this_page_url = mytags_url
	else:
		page_title += " (top)"
		rss_url = '/projects/rss/' + (is_completed and 'completed' or 'proposed') + '/top/' + qs
		this_page_url = top_url
		if is_completed:
			projects = projects.order_by('-score_completed')
		else:
			projects = projects.order_by('-score_proposed')
	
	# For RSS feeds
	if return_raw_projects:
		return page_title, this_page_url, projects
	
	# ...
	list_paginator_page = get_paginator_page(request, projects, PROJECTS_PER_PAGE)
	
	return render_to_response('projects/project_list.html',
			{'project_list_page':list_paginator_page,
			'page_title': page_title,
			'filter_description': filter_description,
			# TODO: also include tags in those urls
			'list_top_url': top_url,
			'list_new_url': new_url,
			'rss_url': rss_url,
			'list_mytags_url': mytags_url},
			context_instance=RequestContext(request))

def list_projects_as_feed(request, completeness, list_type='top'):
	page_title, url, projects = list_projects(request, list_type, completeness=='completed', return_raw_projects=True)
	
	f = feedgenerator.Rss201rev2Feed(
			title=page_title,
			link="http://www.clusterify.com"+url,
			description=u"",
			language=u"en")

	to_print = projects[0:min(ITEMS_IN_FEED, projects.count())]
	for p in to_print:
		f.add_item(title=p.title, 
				link="http://www.clusterify.com"+p.get_absolute_url(), 
				description=p.description_html,
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
		project_members = [u for u in project.joined_users.all()]
		project_members += [project.author]
	
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
	
	return render_to_response('projects/project.html', 
					{'project':project,
					'similar_projects':similar_projects,
					'user_project_status':project.join_status(user),
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
										'comment': comment}))
			
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
# Seed related

def list_seeds(request, list_type='new'):
	seeds = Seed.objects.all()
	
	page_title = "List of project seeds"
	
	if list_type=='top':
		page_title += " (top)"
		seeds = seeds.order_by('-score')
	else:
		page_title += " (new)"
		seeds = seeds.order_by('-pub_date')
	
	paginated_seeds = get_paginator_page(request, seeds, SEEDS_PER_PAGE)
	
	return render_to_response('projects/seed_list.html',
			{'page_title': page_title,
			'paginated_seeds': paginated_seeds,
			'seed_form': SeedForm()},
			context_instance=RequestContext(request))

def post_seed(request):
	user = request.user

	if request.method == 'POST':
		seed_form = SeedForm(request.POST)
		if seed_form.is_valid():
			title = seed_form.cleaned_data['title']
			anonymous = seed_form.cleaned_data['anonymous']
			author_string = seed_form.cleaned_data['author_string']
			
			seed = Seed(title=title, anonymous=anonymous, author_string=author_string)
			if user.is_authenticated():
				seed.author_user = user
				user.message_set.create(message="The project seed you proposed was added to the list.")
			elif not author_string:
				seed.anonymous = True
			
			# TODO: display message to non-authenticated user
			
			seed.save()
			
			return HttpResponseRedirect('/projects/seeds/')
	else:
		seed_form = SeedForm()
		
	return render_to_response('projects/seed_form.html',
			{'form': seed_form},
			context_instance=RequestContext(request))

def seed_to_project(request, seed_pk):
	seed = get_object_or_404(Seed, pk=seed_pk)
	
	# initialize the form with the seed title
	form = ProjectForm(initial={'title': seed.title})
	
	return render_to_response('projects/add_or_edit_project.html',
		{'form': form,
		'is_editing': False},
		context_instance=RequestContext(request))
	
@login_required
def vote_for_seed(request, seed_pk):
	user = request.user
	seed = get_object_or_404(Seed, pk=seed_pk)
	
	try:
		seed.add_vote(user)
	except:
		user.message_set.create(message="You have already voted for this item.")
	
	return HttpResponseRedirect('/projects/seeds/list/?page='+request.GET.get('page','1'))

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

		# only a project's author can edit it
		if(not user == project.author):
			return render_to_response('oops.html', {},
			context_instance=RequestContext(request))
		

	if request.method == 'POST':
		if is_add:
			project = Project(author=user)
		elif project.author != user:
			return render_to_response('oops.html', {},
				context_instance=RequestContext(request))
		
		form = ProjectForm(request.POST)
		if form.is_valid():
			project.title = form.cleaned_data['title']
			project.description_markdown = form.cleaned_data['description']
			if form.cleaned_data['time_estimate']:
				project.hour_estimate = form.cleaned_data['time_estimate']
			if project.p_completed:
				project.showcase_markdown = form.cleaned_data['showcase']
			
			tags = form.cleaned_data['tags']
			
			project.save()
			
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
def set_completed_confirm(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	
	# only a project's author can edit it
	if(not user == project.author):
		return render_to_response('oops.html', {},
		       context_instance=RequestContext(request))
	
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
		return render_to_response('oops.html', {},
		       context_instance=RequestContext(request))

	project.p_completed = True
	project.save()
	
	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def join_project(request, project_author, project_pk):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	project.add_interested_user(user)
	
	project_notification(project, user, "Clusterify -- user wants to join project",
				render_to_string('projects/emails/author_approve_join.txt',
								{ 'project': project,
								'joining_user': user}), True)

	return HttpResponseRedirect(project.get_absolute_url())

@login_required
def approve_join(request, project_author, project_pk, joining_username):
	user = request.user
	project = get_object_or_404(Project, pk=project_pk)
	joining_user = get_object_or_404(User, username=joining_username)
	
	if(user == project.author):
		project.join_user(joining_user)
		project.remove_interested_user(joining_user)
		
		project_notification(project, None, "Clusterify -- new user joined project",
			render_to_string('projects/emails/join_approved.txt',
							{ 'project': project,
							'joining_user': joining_user}))
	
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
