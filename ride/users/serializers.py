import jwt
from datetime import timedelta

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

# Django REST framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from ride.users.models import User, Profile

class ProfileModelSerializer(serializers.ModelSerializer):
    """Profile modal serializer"""

    class Meta:
        model = Profile
        fields = ("picture", "biography", "rides_taken", "rides_offered", "reputation")
        read_only_fields = ("rides_taken", "rides_offered", "reputation")

class UserModelSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "profile")


class UserLoginSerializer(serializers.Serializer):
    """
    Handle the login request data
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Check credentials"""
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        self.context["user"] = user
        if not user.is_verified:
            raise serializers.ValidationError("Account is not active yet")
        return data

    def create(self, data):
        token, created = Token.objects.get_or_create(user=self.context["user"])
        return self.context["user"], token.key


class UserSignUpSerializer(serializers.Serializer):
    """
    Handle sign up data validation and user and profile creation
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    phone_regex = RegexValidator(
        regex=r"\+?1?\d{9,15}$",
        message="Phone number must be in format: +123456789... up to 15 digits",
    )
    phone = serializers.CharField(validators=[phone_regex])

    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        passwd = data["password"]
        passwd_conf = data["password_confirmation"]
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords does not match")
        password_validation.validate_password(passwd)
        return data

    def create(self, data):
        data.pop("password_confirmation")
        user = User.objects.create_user(**data, is_verified=False, is_client=True)
        Profile.objects.create(user=user)
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        """Send account verification link to given user"""
        verification_token = self.generate_verification_email(user)
        subject = f"Welcome @{user.username} Verify your account to start using Ride"
        from_email = "ride <noreply@example.com>"
        content = render_to_string(
            "users/account_verification.html",
            {"token": verification_token, "user": user},
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

    def generate_verification_email(self, user):
        """Create JWT token that user can use to verify its account"""
        exp_date = timezone.now() + timedelta(days=3)
        payload = {
            "user": user.username,
            "exp": int(exp_date.timestamp()),
            "type": "email_confirmation",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token


class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer"""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verify if token is valid"""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Verification link expired")
        except jwt.exceptions.PyJWTError:
            raise serializers.ValidationError("Invalid token")
        if payload["type"] != "email_confirmation":
            raise serializers.ValidationError("Invalid token")

        self.context["payload"] = payload
        return data

    def save(self):
        """Update user's verified status"""
        payload = self.context["payload"]
        user = User.objects.get(username=payload["user"])
        user.is_verified = True
        user.save()

# {
#     "email": "camilo@nunez.com",
#     "username": "camilo",
#     "phone": "3165203926",
#     "password": "admin1234.",
#     "password_confirmation": "admin1234.",
#     "first_name": "camilo",
#     "last_name": "nunez"
# }

# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiY2FtaWxvIiwiZXhwIjoxNjM4Njc1NDExLCJ0eXBlIjoiZW1haWxfY29uZmlybWF0aW9uIn0.TJ_dWnjpJeuwbfyVSdDkZIePcsmrXoIL2tycpSGUAYw

# 44b4c6c090683b6c9f81318c045f0c9398b4a39b

# http -f PATCH localhost:8000/users/camsky/profile/ picture@/Users/andresnunez/Downloads/picture.png "Authorization: Token 44b4c6c090683b6c9f81318c045f0c9398b4a39b" -b