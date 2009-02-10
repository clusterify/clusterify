from django import forms

class ProjectForm(forms.Form):
	title = forms.CharField()
	time_estimate = forms.IntegerField(min_value=1, required=False)
	description = forms.CharField(required=False, widget=forms.widgets.Textarea(attrs={'class':'markdown_textarea','rows':'20'}))
	tags = forms.CharField(required=False)
	#required_tags = forms.CharField(required=False)
	#description_tags = forms.CharField(required=False)

class CommentForm(forms.Form):
	text = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':'5','style':'width:90%'}), max_length=500)
