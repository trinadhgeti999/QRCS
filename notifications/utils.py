"""
Utility functions for notifications app.
"""
# Make channels optional - only import if available
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False
    get_channel_layer = None
    async_to_sync = None

from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def create_notification(recipient=None, recipient_role=None, incident=None, notification_type='message', title='', message=''):
    """
    Create a notification and send via WebSocket.
    
    Args:
        recipient: User instance to receive notification
        recipient_role: Role to send notification to all users with this role
        incident: Incident instance (optional)
        notification_type: Type of notification
        title: Notification title
        message: Notification message
    """
    notifications_created = []
    
    if recipient:
        # Send to specific user
        notification = Notification.objects.create(
            recipient=recipient,
            incident=incident,
            notification_type=notification_type,
            title=title,
            message=message
        )
        notifications_created.append(notification)
        send_websocket_notification(recipient.id, notification)
    
    elif recipient_role:
        # Send to all users with specific role
        users = User.objects.filter(role=recipient_role, is_active=True)
        for user in users:
            notification = Notification.objects.create(
                recipient=user,
                incident=incident,
                notification_type=notification_type,
                title=title,
                message=message
            )
            notifications_created.append(notification)
            send_websocket_notification(user.id, notification)
    
    return notifications_created


def send_websocket_notification(user_id, notification):
    """Send notification via WebSocket."""
    if not CHANNELS_AVAILABLE:
        # Channels not installed - skip WebSocket notification
        return
    
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type': 'notification_message',
                    'data': {
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'notification_type': notification.notification_type,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat(),
                        'incident_id': notification.incident.incident_id if notification.incident else None,
                    }
                }
            )
    except Exception as e:
        # Log error but don't fail notification creation
        print(f"Error sending WebSocket notification: {e}")

