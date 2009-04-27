from clusterify.utils import oops, get_paginator_page
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from eventapp.models import Comment
from eventapp.models import Event
from forms import CommentForm
from forms import EventForm
from projects.models import Project
from tagging.models import TaggedItem

EVENTS_PER_PAGE = 10


def list_events(request, list_type='upcoming', return_raw_events=False):
	events = None
	tags = request.GET.get('tags', "")

	this_page_url = "/events/"
	filter_description = ""

	if list_type == 'upcoming':
		events = Event.objects.filter(end_date__gte=datetime.now())
		page_title = "Upcoming events"
	else:
		events = Event.objects.filter(end_date__lte=datetime.now())
		page_title = "Past events"

	if tags != "":
		events = TaggedItem.objects.get_by_model(Event, tags)
		filter_description += "<li>tags: %s</li>" % tags

	# For RSS feeds
	if return_raw_events:
		return page_title, this_page_url, events, list_type

	list_paginator_page = get_paginator_page(request, events, EVENTS_PER_PAGE)

	return render_to_response('event_list.html', {
		'event_list_page':list_paginator_page,
		'page_title': page_title,
		'list_type': list_type,
		'filter_description': filter_description
		}, context_instance=RequestContext(request))

def list_past_events(request, list_type="past"):
	return list_events(request, list_type)

def list_upcoming_events(request, list_type="upcoming"):
	return list_events(request, list_type)


@login_required
def add_event(request):
	return add_or_edit_event(request, is_add=True)

@login_required
def add_or_edit_event(request, event_pk=None, is_add=False):
	user = request.user
	event = None

	if not is_add:
		event = get_object_or_404(Event, pk=event_pk)
		if event.is_expired():
			user.message_set.create(message="You cannot edit an expired event.")
			return HttpResponseRedirect("/events/")
		if(not user == event.promoter):
			user.message_set.create(message="Only an event's promoter can edit it.")
			return HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))

	if request.method == 'POST':
		if is_add:
			event = Event(promoter=user)
		elif event.promoter != user:
			return oops(request, "Only a event's promoter can edit it.")

		form = EventForm(request.POST, request.FILES)

		if form.is_valid():

			event.name = form.cleaned_data['name']
			if 'image' in request.FILES: 
				file = request.FILES['image']   
				file_content = ContentFile(request.FILES['image'].read())
				event.image.save(request.FILES['image'].name, file_content)
			event.start_date = form.cleaned_data['start_date']
			event.end_date = form.cleaned_data['end_date']
			event.description_markdown = form.cleaned_data['description']
			event.rsvp_link = form.cleaned_data['rsvp_link']
			tags = form.cleaned_data['tags']
			event.save()
			event.set_tags(tags)

			return HttpResponseRedirect(event.get_absolute_url())
	elif not is_add:

		form = EventForm(initial={
			'name':event.name,
			'description':event.description_markdown,
			'image':event.image,
			'start_date':event.start_date,
			'end_date':event.end_date,
			'tags':event.get_editable_tags,
			'rsvp_link':event.rsvp_link,
		})
	else:
		form = EventForm()

	return render_to_response('add_or_edit_event.html',
		{'form': form,
		'is_editing': not is_add,
		'page_title': (is_add and "Add" or "Edit") + " an Event",
		'event': event},
		context_instance=RequestContext(request))


def single_event(request, year, month, day, slug=None, comment_form=CommentForm()):
	user = request.user
	event = get_object_or_404(Event, slug=slug)
	projects = Project.objects.filter(event=event)

	similar_events = TaggedItem.objects.get_related(event, Event, 3)

	return render_to_response('event.html', {
		'event':event,
		'similar_events':similar_events,
		'projects':projects,
		'form':comment_form,
		}, context_instance=RequestContext(request))



@login_required
def post_event_comment(request, event_pk):
	user = request.user
	event = get_object_or_404(Event, pk=event_pk)

	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			text = comment_form.cleaned_data['text']
			comment = Comment(text=text, author=user, event=event)
			comment.save()

			return HttpResponseRedirect(event.get_absolute_url())
	else:
		comment_form = CommentForm()

	return single_project(request, project_author, project_pk, comment_form)

@login_required
def edit_event_comment(request, comment_pk):
	comment = get_object_or_404(Comment, pk=comment_pk)
	
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)

		if comment_form.is_valid():
			comment.text = comment_form.cleaned_data['text']
			comment.save()
			
			return HttpResponseRedirect(comment.get_edit_url())
	else:
		comment_form = CommentForm(initial={'text':comment.text})

	return render_to_response('edit_comment.html',{
			'comment':comment,
			'form':comment_form
		}, context_instance=RequestContext(request))