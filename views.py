from django.http import HttpResponse

from tagging.models import Tag


def tags_js(request):
	tags_array = ["'" + t.name + "'" for t in Tag.objects.all()]

	return HttpResponse("site_tags = [" + ','.join(tags_array) + "]")

def hide_announcement(request):
	request.session['hide_announcement'] = True
	request.session['hmmhmm'] = 'yeah'
	
	return HttpResponse("")

def should_hide_announcement(request):
	return {'hide_announcement': request.session.get('hide_announcement', False), 'wtf': request.session.get('hmmhmm')}

