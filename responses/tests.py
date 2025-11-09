"""
Tests for responses app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from incidents.models import Incident, IncidentCategory
from .models import ResponseTeam, ResponseLog

User = get_user_model()


class ResponseModelTest(TestCase):
    """Test cases for Response models."""
    
    def setUp(self):
        """Set up test data."""
        self.reporter = User.objects.create_user(
            username='reporter',
            password='testpass123',
            role='reporter'
        )
        self.responder = User.objects.create_user(
            username='responder',
            password='testpass123',
            role='responder'
        )
        self.category = IncidentCategory.objects.create(
            name='Fire',
            priority_level=5
        )
        self.incident = Incident.objects.create(
            title='Test Incident',
            description='Test Description',
            category=self.category,
            reporter=self.reporter,
            latitude=40.7128,
            longitude=-74.0060,
            location_address='Test Address'
        )
    
    def test_response_team_creation(self):
        """Test response team creation."""
        team = ResponseTeam.objects.create(
            incident=self.incident,
            responder=self.responder,
            assigned_by=self.reporter
        )
        self.assertEqual(team.incident, self.incident)
        self.assertEqual(team.responder, self.responder)
        self.assertFalse(team.is_lead)
    
    def test_response_log_creation(self):
        """Test response log creation."""
        log = ResponseLog.objects.create(
            incident=self.incident,
            responder=self.responder,
            action='Arrived at scene',
            details='Responder arrived at the incident location'
        )
        self.assertEqual(log.incident, self.incident)
        self.assertEqual(log.action, 'Arrived at scene')


