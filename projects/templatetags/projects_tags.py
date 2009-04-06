"""
"The contents of this file are subject to the Common Public Attribution
License Version 1.0 (the "License"); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at 
http://www.clusterify.com/files/CODE_LICENSE.txt. The License is based 
on the Mozilla Public License Version 1.1 but Sections 14 and 15 have 
been added to cover use of software over a computer network and provide 
for limited attribution for the Original Developer. In addition, Exhibit 
A has been modified to be consistent with Exhibit B.

Software distributed under the License is distributed on an "AS IS" basis, 
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
for the specific language governing rights and limitations under the 
License.

The Original Code is Clusterify.

The Initial Developer of the Original Code is "the Clusterify.com team", 
which is described at http://www.clusterify.com/about/. All portions of 
the code written by the Initial Developer are Copyright (c) the Initial 
Developer. All Rights Reserved.
"""

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

