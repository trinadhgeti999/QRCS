"""
Tests for incidents app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Incident, IncidentCategory

User = get_user_model()


class IncidentModelTest(TestCase):
    """Test cases for Incident models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='reporter'
        )
        self.category = IncidentCategory.objects.create(
            name='Fire',
            priority_level=5,
            description='Fire incidents'
        )
    
    def test_incident_creation(self):
        """Test incident creation."""
        incident = Incident.objects.create(
            title='Test Incident',
            description='Test Description',
            category=self.category,
            reporter=self.user,
            latitude=40.7128,
            longitude=-74.0060,
            location_address='Test Address'
        )
        self.assertTrue(incident.incident_id.startswith('INC'))
        self.assertEqual(incident.status, 'reported')
        self.assertEqual(incident.severity, 'medium')
    
    def test_incident_id_generation(self):
        """Test incident ID generation."""
        incident = Incident.objects.create(
            title='Test',
            description='Test',
            category=self.category,
            reporter=self.user,
            latitude=0,
            longitude=0,
            location_address='Test'
        )
        self.assertIsNotNone(incident.incident_id)
        self.assertEqual(len(incident.incident_id), 19)  # INC + 16 digits
    
    def test_category_creation(self):
        """Test category creation."""
        self.assertEqual(self.category.name, 'Fire')
        self.assertEqual(self.category.priority_level, 5)


