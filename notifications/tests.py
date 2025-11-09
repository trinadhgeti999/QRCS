"""
Tests for notifications app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from incidents.models import Incident, IncidentCategory
from .models import Notification

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='reporter'
        )
        self.category = IncidentCategory.objects.create(
            name='Fire',
            priority_level=5
        )
        self.incident = Incident.objects.create(
            title='Test Incident',
            description='Test Description',
            category=self.category,
            reporter=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            location_address='Test Address'
        )
    
    def test_notification_creation(self):
        """Test notification creation."""
        notification = Notification.objects.create(
            recipient=self.user,
            incident=self.incident,
            notification_type='incident_created',
            title='Test Notification',
            message='Test message'
        )
        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, 'incident_created')


