# Django REST framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Models
from ride.circles.models import Circle
from ride.circles.models.memberships import Membership

# Serializers
from ride.circles.serializers import MembershipSerializer

# Permissions
from rest_framework.permissions import IsAuthenticated
from ride.circles.permissions import IsActiveCircleMember
from ride.circles.permissions.memberships import IsAdminOrMembershipOwner


class MembershipViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Circle membership viewset"""

    serializer_class = MembershipSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists"""
        slug_name = kwargs["slug_name"]
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ["destroy"]:
            permissions.append(IsAdminOrMembershipOwner)
        return [p() for p in permissions]

    def get_queryset(self):
        """Return circle members"""
        return Membership.objects.filter(circle=self.circle, is_active=True)

    def get_object(self):
        """Return the circle member by using the user's username"""
        # import pdb; pdb.set_trace()
        return get_object_or_404(
            Membership,
            user__username=self.kwargs["pk"],
            circle=self.circle,
            is_active=True,
        )

    def perform_destroy(self, instance):
        """Disable membership"""
        instance.is_active = False
        instance.save()
