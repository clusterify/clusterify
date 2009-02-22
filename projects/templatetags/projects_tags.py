from django import template

from projects.models import Seed

register = template.Library()

class VotedOnSeedNode(template.Node):
	def __init__(self, var_name, user_var_name, seed_var_name):
		self.var_name = var_name
		self.user_var_name = user_var_name
		self.seed_var_name = seed_var_name
		
	def render(self, context):
		user = template.Variable(self.user_var_name).resolve(context)
		seed = template.Variable(self.seed_var_name).resolve(context)
		
		if user.is_authenticated():
			context[self.var_name] = seed.user_voted(user)
		else:
			context[self.var_name] = False
		return ''

def do_voted_on_seed(parser, token):
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
	
	return VotedOnSeedNode(bits[5], bits[1], bits[3])


register.tag('user_voted_on_seed', do_voted_on_seed)

