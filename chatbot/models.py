from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    """
    Model to store project data mirrored from Google Sheets.
    This is optional and can be used for caching if needed.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, 
                              choices=[('active', 'Active'), 
                                      ('completed', 'Completed'),
                                      ('on_hold', 'On Hold'),
                                      ('cancelled', 'Cancelled')])
    
    def __str__(self):
        return self.name
    
    @property
    def budget_status(self):
        if self.expenses > self.budget:
            return "over_budget"
        else:
            return "under_budget"
    
    @property
    def remaining_budget(self):
        return self.budget - self.expenses


class ProjectMember(models.Model):
    """
    Model to store project members mirrored from Google Sheets.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.role} ({self.project.name})"
    
class UserProfile(models.Model):
    """
    Extended user profile for associating with projects
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    projects = models.ManyToManyField(Project, related_name='users', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
