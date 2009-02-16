from django.contrib import admin
from models import Project

class ProjectAdmin(admin.ModelAdmin):
	list_display = ['author','title']
	
class CommentAdmin(admin.ModelAdmin):
	list_display = ['author','text']

admin.site.register(Project, ProjectAdmin)
admin.site.register(Comment, CommentAdmin)

