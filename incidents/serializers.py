"""
Serializers for incidents app.
"""
from rest_framework import serializers
from .models import Incident, IncidentCategory
from accounts.serializers import UserSerializer


class IncidentCategorySerializer(serializers.ModelSerializer):
    """Serializer for IncidentCategory model."""
    class Meta:
        model = IncidentCategory
        fields = '__all__'
        read_only_fields = ['created_at']


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer for Incident model."""
    reporter_details = UserSerializer(source='reporter', read_only=True)
    category_details = IncidentCategorySerializer(source='category', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['incident_id', 'reporter', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create incident with current user as reporter."""
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class IncidentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating incident status."""
    status = serializers.ChoiceField(choices=Incident.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


