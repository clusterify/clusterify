from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent, Visitor

admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor)