# Django REST Framework
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

# Permissions
from ride.circles.permissions import IsCircleAdmin

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

# Serializers
from ride.circles.serializers import CircleModelSerializer

# Models
from ride.circles.models import Circle, circles
from ride.circles.models.memberships import Membership


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    serializer_class = CircleModelSerializer
    lookup_field = "slug_name"

    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ("slug_name", "name")
    filter_fields = ("verified", "is_limited")
    ordering_fields = (
        "rides_offered",
        "rides_taken",
        "name",
        "creater",
        "members_limit",
    )
    ordering = ("-members__count", "-rides_offered", "-rides_taken")

    # {{host}}/circles/?verified=1&limit=10&ordering=name&search=UNAM&is_limited=false

    def get_queryset(self):
        queryset = Circle.objects.all()
        if self.action == "list":
            return queryset.filter(is_public=True)
        return queryset

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated]
        if self.action in ["update", "partial_update"]:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        """Assign circle admin"""
        circle = serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10,
        )
