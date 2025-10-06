from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
    ]
    
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
        ('personal', 'Personal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    text = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='personal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.text}"
    
    @property
    def is_today(self):
        if self.due_date:
            return self.due_date == timezone.now().date()
        return False
    
    @property
    def is_tomorrow(self):
        if self.due_date:
            tomorrow = timezone.now().date() + timedelta(days=1)
            return self.due_date == tomorrow
        return False
    
    @property
    def is_upcoming(self):
        if self.due_date:
            tomorrow = timezone.now().date() + timedelta(days=1)
            return self.due_date > tomorrow
        return False
    
    @property
    def priority_color(self):
        colors = {
            'low': '#4CAF50',      # Green
            'medium': '#FF9800',   # Orange  
            'high': '#F44336',     # Red
        }
        return colors.get(self.priority, '#9E9E9E')
    
    @property
    def category_color(self):
        colors = {
            'work': '#2196F3',     # Blue
            'home': '#4CAF50',     # Green
            'personal': '#9C27B0', # Purple
        }
        return colors.get(self.category, '#607D8B')
    
    @property
    def category_icon(self):
        icons = {
            'work': '💼',
            'home': '🏠',
            'personal': '👤',
        }
        return icons.get(self.category, '📝')
    
    class Meta:
        ordering = ['due_date', '-created_at']
