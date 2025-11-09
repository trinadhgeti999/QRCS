"""
Models for notifications app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from incidents.models import Incident

User = get_user_model()


class Notification(models.Model):
    """Model for user notifications."""
    TYPE_CHOICES = [
        ('incident_created', 'Incident Created'),
        ('incident_assigned', 'Incident Assigned'),
        ('status_update', 'Status Update'),
        ('message', 'Message'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


