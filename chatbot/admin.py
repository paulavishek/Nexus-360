from django.contrib import admin
from .models import Project, ProjectMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'budget', 'expenses', 'budget_status')
    list_filter = ('status', )
    search_fields = ('name', 'description')

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'project', 'email')
    list_filter = ('role', 'project')
    search_fields = ('name', 'email', 'role')
