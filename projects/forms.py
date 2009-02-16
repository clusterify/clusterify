from django import forms

class ProjectForm(forms.Form):
	title = forms.CharField(required=True, max_length=200)
	time_estimate = forms.IntegerField(min_value=1, required=False)
	description = forms.CharField(
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
				regex=r'^[A-Za-z0-9\- ]+$')

class CommentForm(forms.Form):
	text = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':'5','style':'width:90%'}), max_length=500)
