from django import template
from projects.models import Project
from django.contrib.auth.models import User


register = template.Library()

class SetContextVarNode(template.Node):
    def __init__(self, var_name, var_value):
		self.var_name = var_name
		self.var_value = var_value
		
    def render(self, context):
        context[self.var_name] = var_value
        return ''

def do_voted_on_seed(user, seed):
    """
    Example usage::

        {% user_voted_on_seed userobj on seedobj as varname %}
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("user_voted_on_seed tag takes exactly 6 arguments")
    if bits[2] != 'on':
        raise template.TemplateSyntaxError("second argument to 'user_voted_on_seed' tag must be 'on'")
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to 'user_voted_on_seed' tag must be 'as'")
    
    user = template.resolve_variable(bits[1])
    seed = template.resolve_variable(bits[3])
    
    return SetContextVarNode(bits[5], seed.user_voted(user))


register.tag('user_voted_on_seed', do_voted_on_seed)


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
