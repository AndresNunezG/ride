# Django REST framework
from rest_framework.permissions import BasePermission

# Models
from ride.circles.models import Membership, memberships


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


class IsAdminOrMembershipOwner(BasePermission):
    """Allow access only to circle admin or users that are owner of the membership"""

    def has_permission(self, request, view):
        membership = view.get_object()
        if membership.user == request.user:
            return True
        try:
            Membership.objects.get(
                circle=view.circle, user=request.user, is_active=True, is_admin=True
            )
        except Membership.DoesNotExist:
            return False
        return True


class IsSelfMember(BasePermission):
    """Allow access only to member owners"""

    def has_permission(self, request, view):
        obj = view.get_object()
        return super().has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
