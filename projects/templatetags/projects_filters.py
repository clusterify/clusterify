from django import template

from projects.models import Seed

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

