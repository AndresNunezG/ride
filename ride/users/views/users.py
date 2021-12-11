# Django REST Framework
from rest_framework import status, viewsets
from rest_framework import permissions
from rest_framework import response
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework.response import Response
# from rest_framework.views import APIView

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from ride.users.permissions import IsAccountOwner

# Serializer
from ride.users.serializers import (
    UserLoginSerializer,
    UserModelSerializer,
    UserSignUpSerializer,
    AccountVerificationSerializer,
)
from ride.circles.serializers import CircleModelSerializer

# Models
from ride.users.models import User
from ride.circles.models.circles import Circle

class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """User view set.
    Handle sign up, login and account verification
    """

    queryset = User.objects.filter(is_active=True, is_client=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permissions based on action"""
        if self.action in ['signup', 'login', 'verify']:
            permissions = [AllowAny]
        elif self.action in ['retrive', 'update', 'partial_update']:
            permissions = [IsAccountOwner, IsAuthenticated]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            "user": UserModelSerializer(user).data,
            "access_token": token,
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        data = {"message": "Congratulations, now go share some Rides!"}
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs)
        circles = Circle.objects.filter(
            members=request.user,
            membership__is_active=True
        )
        data = {
            'user': response.data,
            'circles': CircleModelSerializer(circles, many=True).data
        }
        response.data = data
        return response

# class UserLoginAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user, token = serializer.save()
#         data = {
#             "user": UserModelSerializer(user).data,
#             "access_token": token,
#         }
#         return Response(data, status=status.HTTP_201_CREATED)


# class UserSignupAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserSignUpSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         data = UserModelSerializer(user).data
#         return Response(data, status=status.HTTP_201_CREATED)


# class AccountVerificationAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = AccountVerificationSerializer(data=request.data)
#         serializer.is_valid()
#         serializer.save()
#         data = {"message": "Congratulations, now go share some Rides!"}
#         return Response(data, status=status.HTTP_200_OK)
