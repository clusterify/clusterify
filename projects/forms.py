from django import forms
from django.template import loader, Context

PROJECT_DESCRIPTION_TEMPLATE_FILE = 'projects/project_description_template.txt'

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
				widget=forms.widgets.TextInput(attrs={'style':'width: 50px;'}))
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
