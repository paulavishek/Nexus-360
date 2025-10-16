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
        
# New models for enhanced chat features

class ChatSession(models.Model):
    """
    Model to store user chat sessions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def get_title(self):
        if self.title:
            return self.title
        
        # If no title, use the first message or a default
        first_message = self.messages.filter(role='user').first()
        if (first_message):
            # Truncate long messages for the title
            title = first_message.content[:30]
            if len(first_message.content) > 30:
                title += "..."
            return title
        return f"Chat {self.id}"
    
    def __str__(self):
        return f"Session {self.id}: {self.get_title()} by {self.user.username}"

class ChatMessage(models.Model):
    """
    Model to store individual chat messages
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    MODEL_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
        ('openai-fallback', 'OpenAI (Fallback)'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=20, choices=MODEL_CHOICES, null=True, blank=True)
    is_starred = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role.capitalize()} message in {self.session}"

class UserPreference(models.Model):
    """
    Model to store user preferences like UI theme, preferred AI model, etc.
    """
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
    ]
    
    DEFAULT_MODEL_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    default_model = models.CharField(max_length=10, choices=DEFAULT_MODEL_CHOICES, default='gemini')
    
    def __str__(self):
        return f"{self.user.username}'s preferences"

class ChatAnalytics(models.Model):
    """
    Model to store analytics data about chat usage
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_analytics')
    date = models.DateField()
    messages_sent = models.IntegerField(default=0)
    gemini_requests = models.IntegerField(default=0)
    openai_requests = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']
        verbose_name_plural = 'Chat analytics'
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.user.username} on {self.date.strftime('%Y-%m-%d')}"
