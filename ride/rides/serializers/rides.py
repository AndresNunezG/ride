from datetime import timedelta

# Django
from django.utils import timezone

# Django Rest Framework
from rest_framework import serializers

# Models
from ride.rides.models import Ride
from ride.circles.models.memberships import Membership
from ride.users.models import User

# Serializers
from ride.users.serializers import UserModelSerializer


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


class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        """Meta class"""

        model = Ride
        fields = "__all__"
        read_only_fields = ("offered_in", "offered_by", "is_active")

    def update(self, instance, validated_data):
        """Allow updates only before departure date"""
        now = timezone.now()
        if instance.departure_date <= now:
            raise serializers.ValidationError("Ongoing rides cannot be modified")
        return super(RideModelSerializer, self).update(instance, validated_data)


# GET request to {{host}}/circles/pycol/rides/?search=170
# RESPONSE
# {
#   "count": 2,
#   "next": null,
#   "previous": null,
#   "results": [
#     {
#       "id": 1,
#       "created": "2021-12-29T21:28:45.272227Z",
#       "modified": "2021-12-29T21:28:45.272248Z",
#       "available_seats": 3,
#       "comments": "",
#       "departure_location": "calle 140",
#       "departure_date": "2021-12-29T22:00:00Z",
#       "arrival_location": "calle 170",
#       "arrival_date": "2021-12-29T22:30:00Z",
#       "rating": null,
#       "is_active": true,
#       "offered_by": 9,
#       "offered_in": 25,
#       "passengers": []
#     },
#     {
#       "id": 2,
#       "created": "2021-12-29T22:26:57.292316Z",
#       "modified": "2021-12-29T22:26:57.292340Z",
#       "available_seats": 3,
#       "comments": "",
#       "departure_location": "calle 140",
#       "departure_date": "2021-12-29T22:30:00Z",
#       "arrival_location": "calle 170",
#       "arrival_date": "2021-12-29T23:00:00Z",
#       "rating": null,
#       "is_active": true,
#       "offered_by": 9,
#       "offered_in": 25,
#       "passengers": []
#     }
#   ]
# }

# PATCH request to {{host}}/circles/pycol/rides/1/
# Body
# {
#     "comments": "ride in Kia car"
# }
# RESPONSE
# {
#   "id": 1,
#   "offered_by": {
#     "username": "camilo",
#     "first_name": "camilo",
#     "last_name": "nunez",
#     "email": "camilo@nunez.com",
#     "phone": "1234567890",
#     "profile": {
#       "picture": null,
#       "biography": "",
#       "rides_taken": 0,
#       "rides_offered": 2,
#       "reputation": 5
#     }
#   },
#   "offered_in": "Python Col",
#   "passengers": [],
#   "created": "2021-12-29T21:28:45.272227Z",
#   "modified": "2021-12-30T16:11:13.008192Z",
#   "available_seats": 3,
#   "comments": "ride in Kia car",
#   "departure_location": "calle 140",
#   "departure_date": "2021-12-29T22:00:00Z",
#   "arrival_location": "calle 170",
#   "arrival_date": "2021-12-29T22:30:00Z",
#   "rating": null,
#   "is_active": true
# }


class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer"""

    passenger = serializers.IntegerField()

    class Meta:
        """Meta class"""

        model = Ride
        fields = ("passenger",)

    def validate_passenger(self, data):
        """Verify passenger exists and is a circle member"""
        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid passenger")

        circle = self.context["circle"]
        # if not Membership.object.filter(
        #     user=user, circle=circle, is_active=True
        # ).exists():
        #     raise serializers.ValidationError("Invalid passenger")
        try:
            membership = Membership.objects.get(
                user=user, circle=circle, is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError(
                "User is not an active member of the circle"
            )

        # user and membership to be used in update method
        self.context["user"] = user
        self.context["membership"] = membership
        return data

    def validate(self, data):
        """Verify rides allow new passengers"""

        ride = self.context["ride"]
        if ride.available_seats < 1:
            raise serializers.ValidationError("Ride is already full")

        if Ride.objects.filter(passengers__pk=data["passenger"]).exists():
            raise serializers.ValidationError("Passenger already in this trip")

        return data

    def update(self, instance, data):
        """Add passenger to ride, and update stats"""
        ride = self.context["ride"]
        user = self.context["user"]
        circle = self.context["circle"]

        # Add passenger to ride
        ride.passengers.add(user)
        # Decrease available seats
        ride.available_seats -= 1

        # User stats
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # Membership
        membership = self.context["membership"]
        membership.rides_taken += 1
        membership.save()

        # Circle
        circle = self.context["circle"]
        circle.rides_taken += 1
        circle.save()

        return ride

# POST request to {{host}}/circles/pycol/rides/1/join/
# BODY void
# {
#   "id": 1,
#   "offered_by": {
#     "username": "camilo",
#     "first_name": "camilo",
#     "last_name": "nunez",
#     "email": "camilo@nunez.com",
#     "phone": "1234567890",
#     "profile": {
#       "picture": null,
#       "biography": "",
#       "rides_taken": 1,
#       "rides_offered": 2,
#       "reputation": 5
#     }
#   },
#   "offered_in": "Python Col",
#   "passengers": [
#     {
#       "username": "camilo",
#       "first_name": "camilo",
#       "last_name": "nunez",
#       "email": "camilo@nunez.com",
#       "phone": "1234567890",
#       "profile": {
#         "picture": null,
#         "biography": "",
#         "rides_taken": 1,
#         "rides_offered": 2,
#         "reputation": 5
#       }
#     },
#     {
#       "username": "camsky",
#       "first_name": "camilo",
#       "last_name": "nunez",
#       "email": "camsky@camsky.com",
#       "phone": "3165203926",
#       "profile": {
#         "picture": "/media/users/pictures/camilo.png",
#         "biography": "Enginner",
#         "rides_taken": 1,
#         "rides_offered": 0,
#         "reputation": 5
#       }
#     }
#   ],
#   "created": "2021-12-29T21:28:45.272227Z",
#   "modified": "2021-12-30T16:11:13.008192Z",
#   "available_seats": 2,
#   "comments": "ride in Kia car",
#   "departure_location": "calle 140",
#   "departure_date": "2021-12-29T22:00:00Z",
#   "arrival_location": "calle 170",
#   "arrival_date": "2021-12-29T22:30:00Z",
#   "rating": null,
#   "is_active": true
# }

class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer"""

    current_time = serializers.DateTimeField()

    class Meta:
        """Meta class"""
        
        model = Ride
        fields = ('is_active', 'current_time')
    
    def validate_current_time(self, data):
        """Verify ride have indeed started"""
        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.ValidationError("Ride has not started  yet")
        return data
