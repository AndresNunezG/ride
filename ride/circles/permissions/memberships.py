# Django REST framework
from rest_framework.permissions import BasePermission

# Models
from ride.circles.models import Membership


class IsActiveCircleMember(BasePermission):
    """Allow access only to circle members
    Expect that the views implementing this permission
    have a 'circle' attribute assigned
    """

    def has_permission(self, request, view):
        """Verify that user is an active member"""
        try:
            Membership.objects.get(
                user=request.user, circle=view.circle, is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True
