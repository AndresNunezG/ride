"""Invitations tests"""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

# Models
from ride.circles.models import Invitation, Circle, Membership
from ride.users.models import User, Profile


class InvitationsManagerTestCase(TestCase):
    """Invitations manager test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name="Pepito",
            last_name="Perez",
            email="pepitop@pepe.co",
            username="pepitop",
            password="admin123",
        )
        self.circle = Circle.objects.create(
            name="College",
            slug_name="college",
            about="Official circle for college",
            verified=True,
        )

    def test_code_generation(self):
        """Random codes should be generated automatically"""
        invitation = Invitation.objects.create(issued_by=self.user, circle=self.circle)
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one"""
        code = "ABC123XYZ"
        invitation = Invitation.objects.create(
            issued_by=self.user, circle=self.circle, code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique, a new one must be created"""
        code = "ABC123XYZ"
        invitation_a = Invitation.objects.create(
            issued_by=self.user, circle=self.circle, code=code
        )
        invitation_b = Invitation.objects.create(
            issued_by=self.user, circle=self.circle, code=code
        )
        self.assertNotEqual(invitation_a.code, invitation_b.code)


class MemberInvitationsAPITestCase(APITestCase):
    """Member invitations manager test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name="Pepito",
            last_name="Perez",
            email="pepitop@pepe.co",
            username="pepitop",
            password="admin123",
        )
        self.profile = Profile.objects.create(user=self.user)
        self.circle = Circle.objects.create(
            name="College",
            slug_name="college",
            about="Official circle for college",
            verified=True,
        )
        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.profile,
            circle=self.circle,
            remaining_invitations=10,
        )

        # Auth
        self.token = Token.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

        # URL
        self.url = "/circles/{}/members/{}/invitations/".format(
            self.circle.slug_name, self.user.username
        )

    def test_response_success(self):
        """Verify request succeed"""
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_invitations_creation(self):
        """Verify invitations are generated if none exist previusly"""
        # Invitations in db must be 0
        self.assertEqual(Invitation.objects.count(), 0)

        # Call member invitations URL
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # Verify new invitations were created
        invitations = Invitation.objects.filter(issued_by=self.user)
        self.assertEqual(invitations.count(), self.membership.remaining_invitations)
        for invitation in invitations:
            self.assertIn(invitation.code, request.data["invitations"])
