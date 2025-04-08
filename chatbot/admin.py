from django.contrib import admin
from .models import Project, ProjectMember, UserProfile

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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_projects')
    search_fields = ('user__username', 'user__email')
    
    def get_projects(self, obj):
        return ", ".join([p.name for p in obj.projects.all()])
    get_projects.short_description = 'Projects'
