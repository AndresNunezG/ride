from django.db import models

from ride.utils.models import RideModel


class Circle(RideModel):
    """Circle model
    A circle is a private group where rides are offered and taken
    by its members. To join a circle a user must receive an unique
    invitation code from an existing circle member
    """

    name = models.CharField("circle name", max_length=50)
    slug_name = models.SlugField(unique=True, max_length=50)

    about = models.CharField("circle description", max_length=255)

    picture = models.ImageField(upload_to="circles/pictures", blank=True, null=True)

    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)

    verified = models.BooleanField(
        "verified circle",
        default=False,
        help_text="Verified circles are also known as official communities",
    )

    is_public = models.BooleanField(
        "public field",
        default=False,
        help_text="Public circles are listed in the main page so everyone know about their existence",
    )

    is_limited = models.BooleanField(
        "limited size circle",
        default=False,
        help_text="Limited circles can grow up to a fixed number of members",
    )
    members_limit = models.PositiveIntegerField(
        "limit of members in the circle",
        default=0,
        help_text="If circle is limited, this will be the limit of the number of members",
    )

    members = models.ManyToManyField('users.User', through='circles.Membership', through_fields=('circle', 'user'))

    def __str__(self):
        return self.name

    class Meta(RideModel.Meta):
        ordering = ["-rides_taken", "-rides_offered"]
