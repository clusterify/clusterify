from django.http import HttpResponse

from tagging.models import Tag

from clusterify.utils import get_full_url

def tags_js(request):
	tags_array = ["'" + t.name + "'" for t in Tag.objects.all()]

	return HttpResponse("site_tags = [" + ','.join(tags_array) + "]")

def site_url_preprocessor(request=None):
	return {'site_url': get_full_url()}

def hide_announcement(request):
	request.session['hide_announcement'] = True
	
	return HttpResponse("")

def should_hide_announcement(request):
	return {'hide_announcement': request.session.get('hide_announcement', False)}

