"""
Admin configuration for responses app.
"""
from django.contrib import admin
from .models import ResponseTeam, ResponseLog


@admin.register(ResponseTeam)
class ResponseTeamAdmin(admin.ModelAdmin):
    """Admin for ResponseTeam model."""
    list_display = ['incident', 'responder', 'is_lead', 'assigned_at', 'assigned_by']
    list_filter = ['is_lead', 'assigned_at']
    search_fields = ['incident__incident_id', 'incident__title', 'responder__username']
    readonly_fields = ['assigned_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('incident', 'responder', 'assigned_by')


@admin.register(ResponseLog)
class ResponseLogAdmin(admin.ModelAdmin):
    """Admin for ResponseLog model."""
    list_display = ['incident', 'responder', 'action', 'timestamp']
    list_filter = ['timestamp', 'action']
    search_fields = ['incident__incident_id', 'action', 'details', 'responder__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('incident', 'responder')


