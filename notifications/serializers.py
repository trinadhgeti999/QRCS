"""
Serializers for notifications app.
"""
from rest_framework import serializers
from .models import Notification
from incidents.serializers import IncidentSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    incident_details = IncidentSerializer(source='incident', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']


