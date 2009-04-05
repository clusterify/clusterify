from django import template
from django.utils.timesince import timesince
from django.conf import settings

register = template.Library()

@register.filter(name='settingbyname')
def settingbyname(setting_name):
	return "test"
	#if hasattr(settings, setting_name):
	#	return str(getattr(settings, setting_name))
	#else:
	#	return ""

@register.filter(name='ago')
def ago(date):
	ago = timesince(date)
	return ago.split(",")[0] + " ago"