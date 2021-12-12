# Django
from django.db import models

# Models
from ride.utils.models import RideModel

# Managers
from ride.circles.managers import InvitationManager


class Invitation(RideModel):
    """Circle invitation
    A circle invitation is a random text that acts as a unique
    code that grantes access to a specific circle. This codes are
    generates by users that are already members of the circle and have a
    'remaining_invitations' value greater than 0
    """

    code = models.CharField(max_length=50, unique=True)

    issued_by = models.ForeignKey(
        "users.User",
        verbose_name=("Invitation sended by"),
        on_delete=models.CASCADE,
        help_text="Circle member that is providind the invitation",
        related_name="issued_by",
    )
    used_by = models.ForeignKey(
        "users.User",
        verbose_name=("Invitation used by"),
        on_delete=models.CASCADE,
        null=True,
        help_text="User that used the code to enter to the circle",
    )

    circle = models.ForeignKey(
        "circles.Circle",
        verbose_name=("Invitation for circle"),
        on_delete=models.CASCADE,
    )

    used = models.BooleanField(verbose_name=("Invitation used"), default=False)
    used_at = models.DateTimeField(verbose_name=("Used at"), blank=True, null=True)

    # Manager
    objects = InvitationManager()

    def __str__(self):
        """Return code and circle"""
        return f"#{self.circle.slug_name}: {self.code}"
