"""
Serializers for responses app.
"""
from rest_framework import serializers
from .models import ResponseTeam, ResponseLog
from incidents.serializers import IncidentSerializer
from accounts.serializers import UserSerializer


class ResponseTeamSerializer(serializers.ModelSerializer):
    """Serializer for ResponseTeam model."""
    incident_details = IncidentSerializer(source='incident', read_only=True)
    responder_details = UserSerializer(source='responder', read_only=True)
    assigned_by_details = UserSerializer(source='assigned_by', read_only=True)
    
    class Meta:
        model = ResponseTeam
        fields = '__all__'
        read_only_fields = ['assigned_at']


class ResponseLogSerializer(serializers.ModelSerializer):
    """Serializer for ResponseLog model."""
    incident_details = IncidentSerializer(source='incident', read_only=True)
    responder_details = UserSerializer(source='responder', read_only=True)
    
    class Meta:
        model = ResponseLog
        fields = '__all__'
        read_only_fields = ['timestamp']


