from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ride.users.models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_client",
    )
    list_filter = ("is_client", "is_staff", "created", "modified")


admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ("user", "reputation", "rides_taken", "rides_offered")
    search_fields = (
        "users__username",
        "user__email",
        "user__first_name",
        "users__last_name",
    )
    list_filter = ("reputation",)

    fieldsets = (
        ("Profile", {"fields": (("user", "picture"), ("biography"))}),
        (
            "Stats",
            {
                "fields": (
                    ("reputation"),
                    ("rides_taken", "rides_offered"),
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (("created", "modified"),),
            },
        ),
    )

    readonly_fields = ("created", "modified")
