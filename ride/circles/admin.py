import csv
from datetime import date, datetime, timedelta

# Django
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

# Model
from ride.circles.models import Circle
from ride.rides.models import Ride


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):

    list_display = ("slug_name", "name", "verified")
    list_filter = ("verified", "is_public", "is_limited", "created")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "slug_name"),
                    ("about", "picture"),
                ),
            },
        ),
        (
            "Stats",
            {
                "fields": (("rides_taken", "rides_offered"),),
            },
        ),
        (
            "Privacy",
            {
                "fields": (
                    ("is_public", "verified"),
                    ("is_limited", "members_limit"),
                ),
            },
        ),
    )

    readonly_fields = ("created", "modified")

    actions = ["make_verified", "make_unverified", "Download today rides"]

    def make_verified(self, request, queryset):
        queryset.update(verified=True)

    make_verified.short_description = "Make selected circle verified"

    def make_unverified(self, request, queryset):
        queryset.update(verified=False)

    make_unverified.short_description = "Make selected circle unverified"

    def download_today_rides(self, request, queryset):
        """Return today's rides"""
        now = timezone.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        end = start + timedelta(days=1)

        rides = Ride.objects.filter(
            offered_in__in=queryset.values_list("id"),
            departure_date__gte=start,
            departure_date__lte=end,
        ).order_by("departure_date")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="today_rides.csv"'
        writer = csv.writer(response)

        writer.writerow(
            ["id", "passengers", "departure_location", "departure_date", "rating"]
        )

        for ride in rides:
            writer.writerow(
                [
                    ride.pk,
                    ride.passengers.count(),
                    ride.departure_location,
                    str(ride.departure_date),
                    ride.arrival_location,
                    str(ride.arrival_date),
                    ride.rating,
                ]
            )

        return response

    download_today_rides.short_description = "Download today rides"
