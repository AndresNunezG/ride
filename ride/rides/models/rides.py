# Django
from django.db import models

# Utilities
from ride.utils.models import RideModel


class Ride(RideModel):
    """Ride model"""

    offered_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    offered_in = models.ForeignKey(
        "circles.Circle", on_delete=models.SET_NULL, null=True
    )

    passengers = models.ManyToManyField("users.User", related_name="passengers")

    available_seats = models.PositiveSmallIntegerField(default=1)
    comments = models.TextField(blank=True)

    departure_location = models.CharField(max_length=255)
    departure_date = models.DateTimeField()
    arrival_location = models.CharField(max_length=255)
    arrival_date = models.DateTimeField()

    rating = models.FloatField(null=True)

    is_active = models.BooleanField(
        "active status",
        default=True,
        help_text="Used for disabling the ride or making it as finished",
    )

    def __str__(self):
        """Ride details"""
        return (
            "{_from} to {to} | {start_day} {start_time} - {end_day} {end_time}".format(
                _from=self.departure_location,
                to=self.arrival_location,
                start_day=self.departure_date.strftime("%a %d %b"),
                start_time=self.departure_date.strftime("%I:%M %p"),
                end_day=self.arrival_date.strftime("%a %d %b"),
                end_time=self.arrival_date.strftime("%I:%M %p"),
            )
        )
