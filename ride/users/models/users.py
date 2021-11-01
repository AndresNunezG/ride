from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Utilities
from ride.utils.models import RideModel


class User(RideModel, AbstractUser):
    """
    User model.
    Extend from Django's Abastract User, change the username field
    to email and add some extra fields.
    """

    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        error_messages={"unique": "A user with that email already exists."},
    )

    phone_regex = RegexValidator(
        regex=r"\+?1?\d{9,15}$",
        message="Phone number must be in format: +123456789... up to 15 digits",
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    is_client = models.BooleanField(
        verbose_name="client status",
        default=True,
        help_text=(
            "Distinguish users and perform queries." "Clients are the main type of user"
        ),
    )

    is_verified = models.BooleanField(
        verbose_name="verified client",
        default=False,
        help_text="Set to true when the user have verified its email address",
    )

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
