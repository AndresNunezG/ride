"""Invitations tests"""

# Django
from django.test import TestCase

# Models
from ride.circles.models import Invitation, Circle
from ride.users.models import User

class InvitationsManagerTestCase(TestCase):
    """Invitations manager test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name='Pepito',
            last_name='Perez',
            email='pepitop@pepe.co',
            username='pepitop',
            password='admin123'
        )
        self.circle = Circle.objects.create(
            name="College",
            slug_name="college",
            about="Official circle for college",
            verified=True
        )
    
    def test_code_generation(self):
        """Random codes should be generated automatically"""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one"""
        code = 'ABC123XYZ'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique, a new one must be created"""
        code = "ABC123XYZ"
        invitation_a = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        invitation_b = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertNotEqual(invitation_a.code, invitation_b.code)
