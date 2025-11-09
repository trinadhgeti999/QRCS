"""
Views for incidents app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt

from .models import Incident, IncidentCategory
from .serializers import IncidentSerializer, IncidentCategorySerializer, IncidentStatusUpdateSerializer
from accounts.models import User
from notifications.utils import create_notification


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula."""
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


class IncidentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for IncidentCategory model (read-only)."""
    queryset = IncidentCategory.objects.all()
    serializer_class = IncidentCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # No pagination for categories


class IncidentViewSet(viewsets.ModelViewSet):
    """ViewSet for Incident model."""
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'severity', 'category']
    search_fields = ['title', 'description', 'location_address', 'incident_id']
    ordering_fields = ['created_at', 'updated_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Incident.objects.select_related('category', 'reporter').all()
        
        if user.role == 'admin':
            return queryset
        elif user.role == 'responder':
            # Responders see incidents assigned to them
            return queryset.filter(response_teams__responder=user).distinct()
        else:
            # Reporters see only their own incidents
            return queryset.filter(reporter=user)
    
    def perform_create(self, serializer):
        """Create incident and notify admins."""
        incident = serializer.save()
        # Notify admins
        admins = User.objects.filter(role='admin', is_active=True)
        for admin in admins:
            create_notification(
                recipient=admin,
                incident=incident,
                notification_type='incident_created',
                title='New Incident Reported',
                message=f'New incident: {incident.title}'
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update incident status."""
        incident = self.get_object()
        serializer = IncidentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        old_status = incident.status
        
        # Validate status transition
        if old_status == 'closed':
            return Response(
                {'error': 'Cannot update closed incident'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incident.status = new_status
        
        # Set resolved_at if status is resolved
        if new_status == 'resolved' and not incident.resolved_at:
            incident.resolved_at = timezone.now()
        
        incident.save()
        
        # Create notification
        create_notification(
            recipient=incident.reporter,
            incident=incident,
            notification_type='status_update',
            title='Incident Status Updated',
            message=f'Your incident {incident.incident_id} status changed from {old_status} to {new_status}'
        )
        
        return Response({
            'status': 'success',
            'incident_id': incident.incident_id,
            'old_status': old_status,
            'new_status': new_status
        })
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get incidents near a location."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 5))  # km
        
        if not lat or not lng:
            return Response(
                {'error': 'lat and lng parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all incidents
        incidents = self.get_queryset()
        nearby_incidents = []
        
        for incident in incidents:
            distance = calculate_distance(lat, lng, incident.latitude, incident.longitude)
            if distance <= radius:
                nearby_incidents.append({
                    'incident': IncidentSerializer(incident).data,
                    'distance_km': round(distance, 2)
                })
        
        # Sort by distance
        nearby_incidents.sort(key=lambda x: x['distance_km'])
        
        return Response(nearby_incidents)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get incident statistics."""
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        queryset = self.get_queryset()
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        
        stats = {
            'total': queryset.count(),
            'by_status': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_severity': dict(queryset.values('severity').annotate(count=Count('id')).values_list('severity', 'count')),
            'recent': queryset.filter(created_at__gte=last_30_days).count(),
        }
        
        return Response(stats)

