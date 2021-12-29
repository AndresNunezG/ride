# Django
from django.utils import timezone

# Django rest-framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Models
from ride.circles.models import Circle, Membership, Invitation

# Serializer
from ride.users.serializers import UserModelSerializer


class CircleSerializer(serializers.Serializer):

    name = serializers.CharField()
    slug_name = serializers.SlugField()
    rides_taken = serializers.IntegerField()
    rides_offered = serializers.IntegerField()
    members_limit = serializers.IntegerField()


class CreateCircleSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=140)
    slug_name = serializers.SlugField(
        max_length=140, validators=[UniqueValidator(Circle.objects.all())]
    )
    about = serializers.CharField(max_length=255, required=False)

    def create(self, data):
        return Circle.objects.create(**data)


class CircleModelSerializer(serializers.ModelSerializer):

    members_limit = serializers.IntegerField(
        required=False, min_value=10, max_value=32000
    )

    is_limited = serializers.BooleanField(default=False)

    class Meta:
        model = Circle
        fields = (
            "name",
            "slug_name",
            "about",
            "rides_offered",
            "rides_taken",
            "verified",
            "is_public",
            "is_limited",
            "members_limit",
        )
        read_only_fields = (
            "is_public",
            "verified",
            "rides_offered",
            "rides_taken",
        )

    def validate(self, data):
        """Ensure both members_limit and is_limited are present"""
        members_limit = data.get("members_limit", None)
        is_limited = data.get("is_limited", False)
        if is_limited ^ bool(members_limit):
            raise serializers.ValidationError(
                "If circles is limited, a member list must be provided"
            )


class MembershipSerializer(serializers.ModelSerializer):
    """Member model serializer"""

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(source="created", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "user",
            "is_admin",
            "is_active",
            "used_invitations",
            "remaining_invitations",
            "invited_by",
            "rides_taken",
            "rides_offered",
            "joined_at",
        )
        read_only_fields = (
            "user",
            "used_invitations",
            "invited_by",
            "rides_taken",
            "rides_offered",
        )


class AddMemberSerializer(serializers.Serializer):
    """Add member serializer

    Handle the addition of a new member to a circle
    Circle object and request must be provided in the context
    """

    invitation_code = serializers.CharField(min_length=8)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, data):
        """validate that user isn't an active member"""
        circle = self.context["circle"]
        user = data
        q = Membership.objects.filter(circle=circle, user=user)
        if q.exists():
            raise serializers.ValidationError("User is already a member of this circle")

    def validate_invitation_code(self, data):
        """validate invitation code"""
        try:
            invitation = Invitation.objects.get(
                code=data, circle=self.context["circle"], used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation code")
        self.context["invitation"] = invitation

    def validate(self, data):
        """validate members limit in circle"""
        circle = self.context["circle"]
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError("Circle has reached its members limit")
        return data

    def create(self, data):
        """Create new circle member"""
        circle = self.context["circle"]
        invitation = self.context["invitation"]
        if data["user"] is None:
            user = self.context["request"].user
        else:
            user = data["user"]
        now = timezone.now()
        # Member creation
        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by,
        )

        # Update invitation
        invitation.used_by = user
        invitation.used = True
        invitation.used_at = now
        invitation.save()

        # Update issued data
        issuer = Membership.objects.get(user=invitation.issued_by, circle=circle)
        issuer.used_invitations += 1
        issuer.remaining_invitations -= 1
        issuer.save()

        return member
