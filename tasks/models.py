from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Model for task categories and tags"""
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    usage_frequency = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['-usage_frequency', 'name']
    
    def __str__(self):
        return self.name

class ContextEntry(models.Model):
    """Model for daily context data (messages, emails, notes)"""
    SOURCE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('notes', 'Notes'),
        ('calendar', 'Calendar'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='context_entries')
    content = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='notes')
    source_title = models.CharField(max_length=200, blank=True, null=True)
    processed_insights = models.JSONField(default=dict, blank=True)  # AI-processed insights
    priority_score = models.FloatField(default=0.0)  # AI-calculated priority
    keywords = models.JSONField(default=list, blank=True)  # Extracted keywords
    sentiment_score = models.FloatField(default=0.0)  # Sentiment analysis
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Context Entries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source_type}: {self.content[:50]}..."

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    priority_score = models.FloatField(default=0.0)  # AI-calculated priority score
    due_date = models.DateTimeField(blank=True, null=True)
    suggested_deadline = models.DateTimeField(blank=True, null=True)  # AI-suggested deadline
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)  # AI-suggested tags
    ai_enhanced_description = models.TextField(blank=True, null=True)  # AI-enhanced description
    context_references = models.ManyToManyField(ContextEntry, blank=True)  # Related context entries
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    class Meta:
        ordering = ['-priority_score', '-created_at']
    
    def __str__(self):
        return self.title
