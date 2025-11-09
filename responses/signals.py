"""
Signals for responses app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ResponseTeam


@receiver(post_save, sender=ResponseTeam)
def handle_response_team_assignment(sender, instance, created, **kwargs):
    """
    Signal handler for ResponseTeam assignment.
    - Auto-updates incident status to 'assigned' when responder is assigned
    - Creates notification for the assigned responder
    """
    if created:  # Only on creation, not update
        incident = instance.incident
        responder = instance.responder
        
        # Auto-update incident status to 'assigned' if currently 'reported'
        if incident.status == 'reported':
            incident.status = 'assigned'
            incident.save(update_fields=['status'])
        
        # Create notification for the assigned responder
        try:
            from notifications.utils import create_notification
            create_notification(
                recipient=responder,
                incident=incident,
                notification_type='incident_assigned',
                title='New Incident Assignment',
                message=f'You have been assigned to incident: {incident.title} (ID: {incident.incident_id})'
            )
        except Exception as e:
            # Log error but don't fail the assignment
            print(f"Error creating notification for assignment: {e}")

