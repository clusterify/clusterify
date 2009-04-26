from django.contrib import admin
from django.conf import settings


from eventapp.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name','start_date','start_date')


admin.site.register(Event, EventAdmin)

