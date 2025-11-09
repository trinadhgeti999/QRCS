"""
Admin configuration for incidents app.
"""
from django.contrib import admin
from .models import Incident, IncidentCategory


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    """Admin for IncidentCategory model."""
    list_display = ['name', 'priority_level', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['priority_level', 'created_at']
    ordering = ['priority_level', 'name']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """Admin for Incident model."""
    list_display = ['incident_id', 'title', 'category', 'status', 'severity', 'reporter', 'created_at']
    list_filter = ['status', 'severity', 'category', 'created_at']
    search_fields = ['incident_id', 'title', 'description', 'location_address']
    readonly_fields = ['incident_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('incident_id', 'title', 'description', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'severity')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_address')
        }),
        ('Metadata', {
            'fields': ('reporter', 'image', 'created_at', 'updated_at', 'resolved_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('category', 'reporter')


