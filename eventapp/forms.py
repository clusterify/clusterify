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
from widgets import DateTimeWidget


class EventForm(forms.Form):
	name = forms.CharField(
				required=True, 
                help_text='Max 200 characters',
				max_length=200, 
				widget=forms.widgets.TextInput(attrs={'style':'width: 95%;'}))
	image = forms.ImageField(label="Event image (width=110px)", widget=forms.FileInput, required=False)

	start_date = forms.DateTimeField(widget = DateTimeWidget()) 
	end_date = forms.DateTimeField(widget = DateTimeWidget()) 
	description =forms.CharField(
				required=False,
                help_text='Max 5k characters. Use the Markdown syntax. Good summary <a href="http://crunchbang.org/wiki/formattingrules/" target="_new">here</a>.',
				widget=forms.widgets.Textarea(
					attrs={'class':'markdown_textarea','rows':'20'}),
				max_length=5000)
	tags = forms.RegexField(
				required=False,
                help_text='Alphanumeric, word junction by dash, separation by space',
				regex=r'^[A-Za-z0-9\- ]+$',
				widget=forms.widgets.TextInput(attrs={'style':'width: 95%;'}))
	class Media:
		css = {            
			'all': ('/files/css/calendar/calendar-blue2.css', '/files/css/forms.css',)    
		}
		js = ('/files/js/calendar/calendar.js',
			'/files/js/calendar/lang/calendar-en.js',
			'/files/js/calendar/calendar-setup.js',
			)

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
