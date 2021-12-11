# Django rest-framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Models
from ride.circles.models import Circle, Membership

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
    joined_at = serializers.DateTimeField(source='created', read_only=True)

    class Meta:
        model = Membership
        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
            'joined_at'
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered'
        )