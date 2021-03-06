from django.db import models


class RideModel(models.Model):
    """
    RideModel acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    every table with the following attributes:
        + created (DateTime): Store the datetime the object was created.
        + modified (DateTime): Store the last datetime the object was modified
    """

    created = models.DateTimeField(
        verbose_name="created at",
        auto_now_add=True,
        help_text="Datetime on which the object was created",
    )

    modified = models.DateTimeField(
        verbose_name="modified at",
        auto_now=True,
        help_text="Datetime on which the object was modified",
    )

    class Meta:
        abstract = True
        get_latest_by = "created"
        ordering = ["-created", "-modified"]
