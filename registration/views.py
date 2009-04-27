"""
Views which allow users to create and activate accounts.
"""

import urllib

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.utils import feedgenerator

from registration.forms import RegistrationForm, ProfileForm, OpenIdRegistrationForm
from registration.models import RegistrationProfile, Profile, OpenIdAssociation

from tagging.models import TaggedItem

from django_openidconsumer.util import from_openid_response

from django.contrib.auth import views as auth_views

from projects.models import Comment, Project
from clusterify.utils import get_paginator_page, get_query, oops, get_full_url

# NOTE: the code of django-registration was heavily modified...
# it almost isn't used anymore, due to the bypass of the activation email process

ITEMS_IN_FEED = 20

##############################################################################
# Mostly the original django-registration code (with bypass of activation)

@login_required
def logout(request):
	# Necessary to wrap in case logged in using OpenId
	request.session['openids'] = []
	
	return auth_views.logout(request, template_name='registration/logout.html')

def activate(request, activation_key,
             template_name='registration/activate.html',
             extra_context=None):
    """
    Activate a ``User``'s account from an activation key, if their key
    is valid and hasn't expired.
    
    By default, use the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    **Required arguments**
    
    ``activation_key``
       The activation key to validate and use for activating the
       ``User``.
    
    **Optional arguments**
       
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``account``
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.
    
    ``expiration_days``
        The number of days for which activation keys stay valid after
        registration.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=context)

def register(request, success_url=None,
             form_class=RegistrationForm,
             template_name='registration/registration_form.html',
             extra_context=None):
    """
    Allow a new user to register an account.
    
    Following successful registration, issue a redirect; by default,
    this will be whatever URL corresponds to the named URL pattern
    ``registration_complete``, which will be
    ``/accounts/register/complete/`` if using the included URLConf. To
    change this, point that named pattern at another URL, or pass your
    preferred URL as the keyword argument ``success_url``.
    
    By default, ``registration.forms.RegistrationForm`` will be used
    as the registration form; to change this, pass a different form
    class as the ``form_class`` keyword argument. The form class you
    specify must have a method ``save`` which will create and return
    the new ``User``.
    
    By default, use the template
    ``registration/registration_form.html``; to change this, pass the
    name of a template as the keyword argument ``template_name``.
    
    **Required arguments**
    
    None.
    
    **Optional arguments**
    
    ``form_class``
        The form class to use for registration.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.
    
    ``success_url``
        The URL to redirect to on successful registration.
    
    ``template_name``
        A custom template to use.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = User.objects.create_user(form.cleaned_data['username'],
                                                form.cleaned_data['email'],
                                                form.cleaned_data['password1'])
            new_user.is_active = True
            new_user.save()
            
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
			
            user.message_set.create(message="Your profile has been successfully created.")
            
            return HttpResponseRedirect('/accounts/profile/')
            
            #return render_to_response('registration/activate.html',
            #                        {},
            #                        context_instance=RequestContext(request))
            
            #new_user = form.save()
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            #return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)











##############################################################################
# THE FOLLOWING LICENSE APPLIES TO THE REST OF THIS FILE
# (the rest of this file contains additions made to the original
# django-registration module for Clusterify)

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




##############################################################################
# Constants

USERS_PER_PAGE = 20
SEARCH_RESULTS_PER_PAGE = 10

##############################################################################
# OpenID-related additions

def openid_login_on_success(request, identity_url, openid_response):
	if 'openids' not in request.session.keys():
		request.session['openids'] = []

	# Eliminate any duplicates
	request.session['openids'] = [
		o for o in request.session['openids'] if o.openid != identity_url
	]
	request.session['openids'].append(from_openid_response(openid_response))

	# TODO
	assoc = OpenIdAssociation.objects.filter(url=identity_url)
	if assoc.count() == 0:
		return HttpResponseRedirect('/openid/register/')
	else:
		auth_user = authenticate(openid_url=identity_url)
		login(request, auth_user)

	next = request.GET.get('next', '').strip()
	if not next or not is_valid_next_url(next):
		next = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')

	return HttpResponseRedirect(next)

def register_from_openid(request):
	if not request.openid:
		return oops("It appears your OpenID session isn't valid. Make sure cookies are activated in your browser settings.")
	
	assocs = OpenIdAssociation.objects.filter(url=str(request.openid))
	if assocs.count() > 0:
		return render_to_response('oops.html',
			{'error_message': "Your OpenID URL is already registered and associated with a username."},
			context_instance=RequestContext(request))
	
	if request.method == 'POST':
		form = OpenIdRegistrationForm(request.POST)
		if form.is_valid():
			
			# not supplying a password, therefore the account
			# cannot be logged in from normal login form
			# (creates an unusable password)
			new_user = User.objects.create_user(form.cleaned_data['username'],
												form.cleaned_data['email'])
			new_user.is_active = True
			new_user.save()

			assoc = OpenIdAssociation(user=new_user, url=str(request.openid))
			assoc.save()
			
			auth_user = authenticate(openid_url=str(request.openid))
			login(request, auth_user)
			
			auth_user.message_set.create(message="Your profile has been successfully created and attached to your OpenID URL.")
            
			return HttpResponseRedirect('/accounts/profile/')
		
	else:
		form = OpenIdRegistrationForm()
    
	return render_to_response('registration/openid_registration_form.html',
								{ 'form': form },
								context_instance=RequestContext(request))

##############################################################################
# User listing

def list_users(request, list_type='new', return_raw_users=False):
	user = request.user
	tags = request.GET.get('tags', "")
	terms = request.GET.get('terms', "")
	
	profiles = None
	
	page_title = "People"
	filter_description = ""
	
	# Filter by tags (comes first since we use TaggedItem.objects.get_by_model)
	if list_type=='recommend':
		# Should not be called without @login_required, so we're sure we have a user
		profile = Profile.objects.get(user=user)
		user_tags = profile.get_tags()
		
		# get all profiles matching >=1 of the user's tags
		profiles = TaggedItem.objects.get_union_by_model(Profile, user_tags)
	elif tags != "":
		profiles = TaggedItem.objects.get_by_model(Profile, tags)
		filter_description += "<li>tags: %s</li>" % tags
	# or select a first crude set of results to be filtered
	else:
		profiles = Profile.objects.all()

	# Filter by search terms
	if terms != "":
		page_title = "Search results for '%s'" % terms
		query = get_query(terms, ['description_markdown','user__username'])
		profiles = profiles.filter(query)
	
	# Order results
	if list_type == 'top':
		profiles = profiles.order_by('-completed_projects_karma')
	else:
		profiles = profiles.order_by('-user__date_joined')
	
	# Prepare query string given filters, for link URLs
	qs = ""
	qs_dict = {}
	if tags:
		qs_dict['tags'] = tags
	if terms:
		qs_dict['terms'] = terms
	if qs_dict:
		qs = "?" + urllib.urlencode(qs_dict)
	
	# For RSS feeds
	if return_raw_users:
		this_page_url = "/accounts/people/" + list_type
		return page_title, this_page_url, profiles, list_type
	
	list_paginator_page = get_paginator_page(request, profiles, USERS_PER_PAGE)
	
	return render_to_response('registration/user_list.html',
			{'profile_list_page':list_paginator_page,
			'page_title': page_title,
            'list_type': list_type,
			'search_results_type':terms and 'profiles' or '',
			'search_terms':terms and terms or '',
			'filter_description': filter_description,
			'list_top_url': '/accounts/people/top/' + qs,
			'list_new_url': '/accounts/people/new/' + qs,
			'list_mytags_url': '/accounts/people/recommend/' + qs},
			context_instance=RequestContext(request))

def list_users_as_feed(request, list_type='new'):
	page_title, url, profiles, list_type = list_users(request, list_type, return_raw_users=True)
	
	f = feedgenerator.Rss201rev2Feed(
			title=page_title + " ("+list_type+")",
			link=get_full_url()+url,
			description=page_title + " ("+list_type+")",
			language=u"en")

	to_print = profiles[0:min(ITEMS_IN_FEED, profiles.count())]
	for p in to_print:
		join_text = p.user.username+" joined on "+str(p.user.date_joined.strftime('%b %d, %Y @ %I:%M%p'))+(p.location and " from "+p.location or "")
		f.add_item(title=join_text,
				link=get_full_url()+p.get_absolute_url(), 
				description="<img src='"+p.get_gravatar_url()+"'>"+join_text,
				pubdate=p.user.date_joined)
	
	return HttpResponse(f.writeString('UTF-8'), mimetype="application/rss+xml")

@login_required
def list_users_mytags(request):
	return list_users(request, "recommend")

##############################################################################
# Profile-related additions

# MODIF: added these two profile-related functions
@login_required
def edit_profile(request):
    user = request.user
    # if it's the first time the user edits his profile, we'll need
    # to create the object
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.save()

            profile.description_markdown = form.cleaned_data['description']
            profile.set_tags(form.cleaned_data['tags'])
            profile.location = form.cleaned_data['location']
            
            profile.save()
            
            return HttpResponseRedirect('/accounts/profile/')
    else:
        form = ProfileForm(
                  initial={
                        'email': user.email,
                        'location': profile.location,
                        'description': profile.description_markdown,
                        'tags': profile.get_editable_tags()})

    return render_to_response('registration/edit_profile.html',
        {'form': form},
        context_instance=RequestContext(request))

def view_profile(request, username):
    try:
        user = User.objects.get(username=username)
        profile, created = Profile.objects.get_or_create(user=user)
        user_tags = profile.get_tags()
        projects_completed = Project.objects.filter(p_completed=True, wont_be_completed=False, author=user)

        # show the last 5 comments and projects in the user's profile
        user_comments = Comment.objects.filter(author=user).order_by('pub_date')
        user_projects = user.projects_authored.order_by('-pub_date')

        return render_to_response('registration/profile.html',
            {'profile':profile,
             'user_tags':user_tags,
             'projects_count':user_projects.count(),
             'projects_completed':projects_completed.count(),
             'comments_count':user_comments.count(),
             'more_than_five_comments':user_comments.count()>5,
             'more_than_five_projects':user_projects.count()>5,
             'comments':user_comments[0:5],
             'projects':user_projects[0:5]},
            context_instance=RequestContext(request))
    except User.DoesNotExist:
        raise Http404
    except Profile.DoesNotExist:
        raise Http404

def view_comments(request, username):
    try:
        user = User.objects.get(username=username)
        user_comments = Comment.objects.filter(author = user)
        return render_to_response('registration/comments.html',
            {'username':user.username,
            'comments':user_comments},
            context_instance=RequestContext(request))
    except User.DoesNotExist:
        raise Http404

def view_projects(request, username):
    try:
        user = User.objects.get(username=username)
        projects_authored = user.projects_authored.all()
        projects_joined = user.projects_joined.all()

        return render_to_response('registration/projects.html',
            {'username':user.username,
             'projects_authored':projects_authored,
             'projects_joined':projects_joined,},
            context_instance=RequestContext(request))
    except User.DoesNotExist:
        raise Http404

@login_required
def view_default_profile(request):
	user = request.user

        # WAS: return view_profile(request, user.username)
        # I think this makes the url more consistent
        return HttpResponseRedirect('/accounts/profile/view/%s/' % user.username)	

