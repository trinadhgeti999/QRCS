"""
Admin configuration for responses app.
"""
from django.contrib import admin
from django import forms
from .models import ResponseTeam, ResponseLog
from accounts.models import User
from incidents.models import Incident


class ResponseTeamAdminForm(forms.ModelForm):
    """Custom form for ResponseTeam with filtered fields."""
    class Meta:
        model = ResponseTeam
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter responder field to only show users with role='responder'
        self.fields['responder'].queryset = User.objects.filter(
            role='responder',
            is_active=True
        ).order_by('username')
        
        # Filter assigned_by field to only show users with role='admin' (Administrator)
        self.fields['assigned_by'].queryset = User.objects.filter(
            role='admin',
            is_active=True
        ).order_by('username')
        
        # Filter incident field to only show incidents with status='reported'
        self.fields['incident'].queryset = Incident.objects.filter(
            status='reported'
        ).order_by('-created_at')


@admin.register(ResponseTeam)
class ResponseTeamAdmin(admin.ModelAdmin):
    """Admin for ResponseTeam model."""
    form = ResponseTeamAdminForm
    list_display = ['incident', 'responder', 'is_lead', 'assigned_at', 'assigned_by']
    list_filter = ['is_lead', 'assigned_at']
    search_fields = ['incident__incident_id', 'incident__title', 'responder__username']
    readonly_fields = ['assigned_at']
    autocomplete_fields = []  # Disable autocomplete to use filtered queryset
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('incident', 'responder', 'assigned_by')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Override to filter foreign key fields."""
        if db_field.name == 'responder':
            # Only show users with role='responder'
            kwargs['queryset'] = User.objects.filter(
                role='responder',
                is_active=True
            ).order_by('username')
        elif db_field.name == 'assigned_by':
            # Only show users with role='admin' (Administrator)
            kwargs['queryset'] = User.objects.filter(
                role='admin',
                is_active=True
            ).order_by('username')
        elif db_field.name == 'incident':
            # Only show incidents with status='reported'
            kwargs['queryset'] = Incident.objects.filter(
                status='reported'
            ).order_by('-created_at')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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


