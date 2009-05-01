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
from django.contrib.auth.models import User

register = template.Library()

def project_count():
    return Project.objects.all().count()

register.simple_tag(project_count)

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

@register.simple_tag
def voted_on_project(request, project, user):
    if user.is_authenticated():
        if project.user_voted_proposed(user):
            return "voted"
        else:
            return "votable"