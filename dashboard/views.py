"""
Views for dashboard app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from incidents.models import Incident
from responses.models import ResponseTeam, ResponseLog
from notifications.models import Notification
from accounts.models import User


class DashboardStatsView(APIView):
    """API view for dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard statistics."""
        user = request.user
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Base queryset based on user role
        if user.role == 'admin':
            incidents_qs = Incident.objects.all()
            response_teams_qs = ResponseTeam.objects.all()
            response_logs_qs = ResponseLog.objects.all()
        elif user.role == 'responder':
            incidents_qs = Incident.objects.filter(response_teams__responder=user).distinct()
            response_teams_qs = ResponseTeam.objects.filter(responder=user)
            response_logs_qs = ResponseLog.objects.filter(responder=user)
        else:
            incidents_qs = Incident.objects.filter(reporter=user)
            response_teams_qs = ResponseTeam.objects.filter(incident__reporter=user)
            response_logs_qs = ResponseLog.objects.filter(incident__reporter=user)
        
        stats = {
            'overview': {
                'total_incidents': incidents_qs.count(),
                'active_incidents': incidents_qs.filter(
                    status__in=['reported', 'assigned', 'in_progress']
                ).count(),
                'resolved_today': incidents_qs.filter(
                    resolved_at__date=now.date()
                ).count(),
                'resolved_this_week': incidents_qs.filter(
                    resolved_at__gte=last_7_days
                ).count(),
            },
            'by_status': dict(
                incidents_qs.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            ),
            'by_severity': dict(
                incidents_qs.values('severity')
                .annotate(count=Count('id'))
                .values_list('severity', 'count')
            ),
            'recent_trend': list(
                incidents_qs.filter(created_at__gte=last_30_days)
                .extra(select={'day': "date(created_at)"})
                .values('day')
                .annotate(count=Count('id'))
                .order_by('day')
            ),
            'response_stats': {
                'total_assignments': response_teams_qs.count(),
                'total_logs': response_logs_qs.count(),
                'active_responders': User.objects.filter(
                    role='responder',
                    is_available=True,
                    is_active=True
                ).count(),
            },
            'notifications': {
                'unread_count': Notification.objects.filter(
                    recipient=user,
                    is_read=False
                ).count(),
                'total_count': Notification.objects.filter(recipient=user).count(),
            }
        }
        
        # Add average response time for admins
        if user.role == 'admin':
            resolved_incidents = incidents_qs.filter(
                status='resolved',
                resolved_at__isnull=False
            )
            if resolved_incidents.exists():
                # Calculate average time to resolve
                response_times = []
                for incident in resolved_incidents:
                    if incident.resolved_at and incident.created_at:
                        delta = incident.resolved_at - incident.created_at
                        response_times.append(delta.total_seconds() / 3600)  # hours
                
                if response_times:
                    stats['overview']['avg_response_time_hours'] = round(
                        sum(response_times) / len(response_times), 2
                    )
        
        return Response(stats)


class IncidentTrendView(APIView):
    """API view for incident trends."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get incident trends over time."""
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        if user.role == 'admin':
            incidents_qs = Incident.objects.all()
        elif user.role == 'responder':
            incidents_qs = Incident.objects.filter(response_teams__responder=user).distinct()
        else:
            incidents_qs = Incident.objects.filter(reporter=user)
        
        start_date = timezone.now() - timedelta(days=days)
        
        trends = list(
            incidents_qs.filter(created_at__gte=start_date)
            .extra(select={'day': "date(created_at)"})
            .values('day')
            .annotate(
                count=Count('id'),
                by_status=Count('id', filter=Q(status='reported')),
                resolved=Count('id', filter=Q(status='resolved'))
            )
            .order_by('day')
        )
        
        return Response(trends)


