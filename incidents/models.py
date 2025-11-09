"""
Models for incidents app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class IncidentCategory(models.Model):
    """Category model for incidents."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    priority_level = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_categories'
        verbose_name = 'Incident Category'
        verbose_name_plural = 'Incident Categories'
        ordering = ['priority_level', 'name']
    
    def __str__(self):
        return self.name


class Incident(models.Model):
    """Incident model for reporting and tracking emergencies."""
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    incident_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(IncidentCategory, on_delete=models.PROTECT, related_name='incidents')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_address = models.CharField(max_length=500)
    
    image = models.ImageField(upload_to='incidents/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'incidents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def save(self, *args, **kwargs):
        """Generate incident_id if not set."""
        if not self.incident_id:
            from datetime import datetime
            self.incident_id = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"


