from django.http import HttpResponse

from tagging.models import Tag


def tags_js(request):
	tags_array = ["'" + t.name + "'" for t in Tag.objects.all()]

	return HttpResponse("site_tags = [" + ','.join(tags_array) + "]")
