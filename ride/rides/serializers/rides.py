from datetime import timedelta

# Django
from django.utils import timezone

# Django Rest Framework
from rest_framework import serializers
from ride.circles.models import memberships

# Models
from ride.rides.models import Ride
from ride.circles.models.memberships import Membership


class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride serializer"""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """Meta class"""

        model = Ride
        exclude = ("offered_in", "passengers", "rating", "is_active")

    def validate_departure_data(self, data):
        """Verify data is not in the past"""
        min_date = timezone.now() + timedelta(minutes=15)
        if data < min_date:
            raise serializers.ValidationError(
                "Departure time must be at least passing the next 15 minutes window"
            )
        return data

    def validate(self, data):
        """Validate
        Verify that the person who offers the ride is member
        and also the same user making the request
        """
        user = self.context["request"].user
        circle = self.context["circle"]

        if user != data["offered_by"]:
            raise serializers.ValidationError(
                "Rides offered on behalf of others are not allowed"
            )

        try:
            membership = Membership.objects.get(
                user=user, circle=circle, is_active=True
            )
            self.context["membership"] = membership
        except Membership.DoesNotExist:
            raise serializers.ValidationError(
                "User is not an active member of the circle"
            )

        if data["arrival_date"] < data["departure_date"]:
            raise serializers.ValidationError(
                "Departure date must happen before arrival date"
            )

        return data

    def create(self, data):
        """Create ride and update stats"""
        circle = self.context["circle"]
        ride = Ride.objects.create(**data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context["membership"]
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = data["offered_by"].profile
        profile.rides_offered += 1
        profile.save()

        return ride


# POST request to <host>/circles/<circle__slug_name>/rides/
# time in format datetime.datetime.now().astimezone().isoformat()
# {
#     "available_seats": 3,
#     "departure_location": "calle 140",
#     "departure_date": "2021-12-29T17:00:00-05:00",
#     "arrival_location": "calle 170",
#     "arrival_date": "2021-12-29T17:30:00-05:00"
# }

# RESPONSE
# {
#   "id": 1,
#   "available_seats": 3,
#   "created": "2021-12-29T21:28:45.272227Z",
#   "modified": "2021-12-29T21:28:45.272248Z",
#   "comments": "",
#   "departure_location": "calle 140",
#   "departure_date": "2021-12-29T22:00:00Z",
#   "arrival_location": "calle 170",
#   "arrival_date": "2021-12-29T22:30:00Z"
# }
