from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter(name='settingbyname')
def settingbyname(setting_name):
	if hasattr(settings, setting_name):
		return str(getattr(settings, setting_name))
	else:
		return ""

@register.filter(name='ago')
def ago(date):
	ago = timesince(date)
	return ago.split(",")[0] + " ago"