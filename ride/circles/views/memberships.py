# Django REST framework
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404

# Models
from ride.circles.models import Circle
from ride.circles.models.memberships import Membership

# Serializers
from ride.circles.serializers import MembershipSerializer

class MembershipViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Circle membership viewset"""

    serializer_class = MembershipSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists"""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(
            Circle, slug_name=slug_name
        )
        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return circle members"""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )