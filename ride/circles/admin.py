# Django
from django.contrib import admin
from django.contrib.admin.filters import ListFilter

# Model
from ride.circles.models import Circle

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):

    list_display = ('slug_name', 'name', 'verified')
    list_filter = ('verified', 'is_public', 'is_limited', 'created')

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "slug_name"),
                    ("about", "picture"),
                ),
            }
        ),
        (
            "Stats",
            {
                "fields": (
                    ("rides_taken", "rides_offered"),
                ),
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