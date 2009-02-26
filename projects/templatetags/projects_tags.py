from django import template

from projects.models import Project

register = template.Library()

class RoleForProjectNode(template.Node):
	def __init__(self, var_name, user_var_name, project_var_name):
		self.var_name = var_name
		self.user_var_name = user_var_name
		self.project_var_name = project_var_name
		
	def render(self, context):
		user = template.Variable(self.user_var_name).resolve(context)
		project = template.Variable(self.project_var_name).resolve(context)
		
		if user.is_authenticated():
			context[self.var_name] = project.member_role(user)
		else:
			context[self.var_name] = False
		return ''

def do_role_for_project(parser, token):
	"""
	Example usage::
		{% role_for_project userobj for projectobj as varname %}
	"""
	bits = token.contents.split()
	if len(bits) != 6:
		raise template.TemplateSyntaxError("role_for_project tag takes exactly 6 arguments")
	if bits[2] != 'for':
		raise template.TemplateSyntaxError("second argument to 'role_for_project' tag must be 'for'")
	if bits[4] != 'as':
		raise template.TemplateSyntaxError("fourth argument to 'role_for_project' tag must be 'as'")
	
	return RoleForProjectNode(bits[5], bits[1], bits[3])


register.tag('role_for_project', do_role_for_project)

