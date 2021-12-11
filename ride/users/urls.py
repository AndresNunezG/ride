from django.urls import path
from django.urls.conf import include, include
from rest_framework import routers

from rest_framework.routers import DefaultRouter

# from ride.users.views import (
#     UserLoginAPIView,
#     UserSignupAPIView,
#     AccountVerificationAPIView,
# )

from ride.users.views import users as user_views

router = DefaultRouter()
router.register(r"users", user_views.UserViewSet, basename="users")

urlpatterns = [path("", include(router.urls))]

# urlpatterns = [
#     path("users/login/", UserLoginAPIView.as_view(), name="login"),
#     path("users/signup/", UserSignupAPIView.as_view(), name="signup"),
#     path("users/verify/", AccountVerificationAPIView.as_view(), name="verify"),
# ]
