"""
Views which allow users to create and activate accounts.
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from registration.forms import RegistrationForm, ProfileForm
from registration.models import RegistrationProfile, Profile
from projects.models import Comment

from progjects.utils import get_paginator_page

USERS_PER_PAGE = 20
SEARCH_RESULTS_PER_PAGE = 10

def list_users(request):
	users = User.objects.all()
		
	list_paginator_page = get_paginator_page(request, users, USERS_PER_PAGE)
	return render_to_response('registration/user_list.html',
			{'user_list_page':list_paginator_page},
			context_instance=RequestContext(request))

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
            
            profile.save()
            
            return HttpResponseRedirect('/accounts/profile/')
    else:
        form = ProfileForm(
                  initial={
                        'email': user.email,
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
        
        # randomly choose 3 of the user's comments & projects
        user_comments = Comment.objects.filter(author=user).order_by('?')[0:3]
        user_projects = user.projects_authored.order_by('?')[0:3]

        return render_to_response('registration/profile.html',
            {'profile':profile,
             'user_tags':user_tags,
             'comments':user_comments,
             'projects':user_projects},
            context_instance=RequestContext(request))
    except User.DoesNotExist:
        raise Http404
    except Profile.DoesNotExist:
        raise Http404

def profile_search(request):
	terms = request.GET.get('terms', '')
	
	error = None
	if terms == '' or len(terms) <= 3:
		error = "Query must be at least 4 characters long"
		
	profile_matches = Profile.search(terms)
	
	paginated_profiles = get_paginator_page(request, profile_matches, SEARCH_RESULTS_PER_PAGE)
	
	return render_to_response('registration/profile_search_results.html',
			{'error': error,
			'search_terms': terms,
			'search_results_type': 'profiles',
			'paginated_profiles': paginated_profiles},
			context_instance=RequestContext(request))

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
            new_user = form.save()
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
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
