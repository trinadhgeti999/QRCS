"""
Models for responses app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from incidents.models import Incident

User = get_user_model()


class ResponseTeam(models.Model):
    """Model for assigning responders to incidents."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='response_teams')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_incidents')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_made'
    )
    
    notes = models.TextField(blank=True)
    is_lead = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'response_teams'
        unique_together = ['incident', 'responder']
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['incident', 'responder']),
        ]
    
    def __str__(self):
        return f"{self.responder.username} -> {self.incident.incident_id}"


class ResponseLog(models.Model):
    """Model for logging response actions."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='response_logs')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='response_logs')
    
    action = models.CharField(max_length=200)
    details = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    image = models.ImageField(upload_to='response_logs/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'response_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['incident', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.incident.incident_id}"


