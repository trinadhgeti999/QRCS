"""
Tests for accounts app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='reporter'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'reporter')
        self.assertTrue(self.user.is_available)
    
    def test_user_str(self):
        """Test user string representation."""
        self.assertIn('testuser', str(self.user))
        self.assertIn('Reporter', str(self.user))


