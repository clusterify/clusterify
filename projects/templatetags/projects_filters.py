from django import template
from projects.models import Project
from django.contrib.auth.models import User

register = template.Library()

def proposed_project_count():
    return Project.objects.filter(p_completed=False, wont_be_completed=False).count()

register.simple_tag(proposed_project_count)

def completed_project_count():
    return Project.objects.filter(p_completed=True, wont_be_completed=False).count()

register.simple_tag(completed_project_count)

def people_count():
    return User.objects.all().count()

register.simple_tag(people_count)

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''
