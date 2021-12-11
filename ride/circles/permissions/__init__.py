from rest_framework.permissions import BasePermission

from ride.circles.models import Membership


class IsCircleAdmin(BasePermission):
    """Allow access only to admin users"""

    def has_object_permission(self, request, view, obj):
        """Verify user have a membership in the obj"""
        try:
            Membership.objects.get(
                user=request.user, circle=obj, is_admin=True, is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True
