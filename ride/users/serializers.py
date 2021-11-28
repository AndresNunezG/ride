# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator

# Django REST framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from ride.users.models import User, Profile


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
        )


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
        validators=[UniqueValidator(queryset=User.objects.all())]
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
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords does not match")
        password_validation.validate_password(passwd)
        return data
    
    def create(self, data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        Profile.objects.create(user=user)
        return user