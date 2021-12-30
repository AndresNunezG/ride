from datetime import timedelta

# Django
from django.utils import timezone

# Django Rest Framework
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Serializers
from ride.rides.serializers import (
    CreateRideSerializer,
    RideModelSerializer,
    JoinRideSerializer,
)

# Models
from ride.circles.models.circles import Circle
from ride.rides.models import Ride

# Permissions
from rest_framework.permissions import IsAuthenticated
from ride.circles.permissions import IsActiveCircleMember
from ride.rides.permissions import IsRideOwner, IsNotRideOnwer

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter


class RideViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    """Rides view set"""

    permission_classes = [IsAuthenticated, IsActiveCircleMember]
    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ("departure_date", "arrival_date", "available_seats")
    ordering_fields = ("departure_date", "arrival_date", "available_seats")
    search_fields = ("departure_location", "arrival_location")

    def dispatch(self, request, *args, **kwargs):
        """Verify that circle exists"""
        slug_name = kwargs["slug_name"]
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ["update", "partial_update"]:
            permissions.append(IsRideOwner)
        if self.action == "join":
            permissions.append(IsNotRideOnwer)
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action"""
        if self.action == "create":
            return CreateRideSerializer
        if self.action in ["update", "partial_update"]:
            return JoinRideSerializer
        return RideModelSerializer

    def get_serializer_context(self):
        """Add circle to serializer context"""
        context = super(RideViewSet, self).get_serializer_context()
        context["circle"] = self.circle
        return context

    def get_queryset(self):
        """Return active circle's rides"""
        # offset = timezone.now() + timedelta(minutes=15)
        # departure_date__gte=offset,
        return Ride.objects.filter(
            is_active=True, available_seats__gte=1, offered_in=self.circle
        )

    @action(detail=True, methods=["post"])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride"""
        # get ride
        ride = self.get_object()
        # partial update in serializer
        serializer = JoinRideSerializer(
            ride,
            data={"passenger": request.user.pk},
            context={"ride": ride, "circle": self.circle},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)
