# Django REST Framework
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify requesting user is the ride creator"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.offered_by


class IsNotRideOnwer(BasePermission):
    """Verify requesting user is not the ride creator"""

    def has_object_permission(self, request, view, obj):
        return request.user != obj.offered_by
