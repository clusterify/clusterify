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

from django import forms
from django.template import loader, Context

PROJECT_DESCRIPTION_TEMPLATE_FILE = 'projects/project_description_template.txt'
ESTIMATE_CHOICES = (
	('1', '1'),
	('2', '2'),
	('3', '3'),
	('4', '4'),
	('5', '5'),
	('10', '10'),
	('15', '15'),
	('24', '24'),
	('40', '40'),
	('50', '50'),
	('75', '75'),
	('100', '100'),
)

def get_description_template():
	return loader.get_template(PROJECT_DESCRIPTION_TEMPLATE_FILE).render(Context({}))

class ProjectForm(forms.Form):
	title = forms.CharField(
				required=True, 
				max_length=200, 
				widget=forms.widgets.TextInput(attrs={'style':'width: 95%;'}))
	time_estimate = forms.IntegerField(
				min_value=1,
				required=False,
				widget=forms.widgets.Select(choices=ESTIMATE_CHOICES))
	not_involved = forms.BooleanField(required=False)
	description = forms.CharField(
				initial=get_description_template, # idea taken at http://andrewwilkinson.wordpress.com/2009/01/28/dynamic-initial-values-in-django-forms/
				required=False,
				widget=forms.widgets.Textarea(
					attrs={'class':'markdown_textarea','rows':'20'}),
				max_length=5000)
	showcase = forms.CharField(
				required=False,
				widget=forms.widgets.Textarea(
					attrs={'class':'markdown_textarea','rows':'15'}),
				max_length=5000)
	tags = forms.RegexField(
				required=False,
				regex=r'^[A-Za-z0-9\- ]+$',
				widget=forms.widgets.TextInput(attrs={'style':'width: 95%;'}))

class JoinForm(forms.Form):
	role = forms.CharField(
				initial='I could work on the XYZ part.',
				required=False,
				widget=forms.widgets.Textarea(
					attrs={'style':'width: 90%;', 'rows':'4'}),
				max_length=120)

class CommentForm(forms.Form):
	text = forms.CharField(
				widget=forms.widgets.Textarea(attrs={'rows':'5','style':'width:90%'}),
				max_length=5000)
