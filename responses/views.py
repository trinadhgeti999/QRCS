"""
Views for responses app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import ResponseTeam, ResponseLog
from .serializers import ResponseTeamSerializer, ResponseLogSerializer
from incidents.models import Incident
from notifications.utils import create_notification


class ResponseTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for ResponseTeam model."""
    queryset = ResponseTeam.objects.all()
    serializer_class = ResponseTeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['incident', 'responder', 'is_lead']
    search_fields = ['incident__incident_id', 'incident__title', 'responder__username']
    ordering_fields = ['assigned_at']
    ordering = ['-assigned_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = ResponseTeam.objects.select_related('incident', 'responder', 'assigned_by').all()
        
        if user.role == 'admin':
            return queryset
        elif user.role == 'responder':
            return queryset.filter(responder=user)
        else:
            return queryset.filter(incident__reporter=user)
    
    def perform_create(self, serializer):
        """Create response team assignment."""
        # Only admins can assign responders
        if self.request.user.role != 'admin':
            raise PermissionDenied("Only admins can assign responders")
        
        serializer.save(assigned_by=self.request.user)
        
        # Update incident status if needed
        incident = serializer.instance.incident
        if incident.status == 'reported':
            incident.status = 'assigned'
            incident.save()
        
        # Notify responder
        create_notification(
            recipient=serializer.instance.responder,
            incident=incident,
            notification_type='incident_assigned',
            title='New Incident Assignment',
            message=f'You have been assigned to incident: {incident.title}'
        )
    
    @action(detail=True, methods=['post'])
    def set_lead(self, request, pk=None):
        """Set responder as team lead."""
        response_team = self.get_object()
        
        # Only admins can set leads
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can set team leads'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove lead status from other responders on same incident
        ResponseTeam.objects.filter(
            incident=response_team.incident,
            is_lead=True
        ).update(is_lead=False)
        
        # Set this responder as lead
        response_team.is_lead = True
        response_team.save()
        
        return Response({'status': 'success', 'is_lead': True})


class ResponseLogViewSet(viewsets.ModelViewSet):
    """ViewSet for ResponseLog model."""
    queryset = ResponseLog.objects.all()
    serializer_class = ResponseLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['incident', 'responder']
    search_fields = ['action', 'details', 'incident__incident_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = ResponseLog.objects.select_related('incident', 'responder').all()
        
        if user.role == 'admin':
            return queryset
        elif user.role == 'responder':
            return queryset.filter(responder=user)
        else:
            return queryset.filter(incident__reporter=user)
    
    def perform_create(self, serializer):
        """Create response log entry."""
        # Only assigned responders can log responses
        incident = serializer.validated_data['incident']
        user = self.request.user
        
        if user.role == 'responder':
            if not ResponseTeam.objects.filter(incident=incident, responder=user).exists():
                raise PermissionDenied("You are not assigned to this incident")
        
        serializer.save(responder=user)
        
        # Notify reporter if responder logs update
        if incident.reporter != user:
            create_notification(
                recipient=incident.reporter,
                incident=incident,
                notification_type='status_update',
                title='Response Update',
                message=f'New update on incident {incident.incident_id}: {serializer.instance.action}'
            )

