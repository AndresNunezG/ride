from django.urls import path

from ride.users.views import UserLoginAPIView, UserSignupAPIView, AccountVerificationAPIView

urlpatterns = [
    path("users/login/", UserLoginAPIView.as_view(), name="login"),
    path("users/signup/", UserSignupAPIView.as_view(), name="signup"),
    path("users/verify/", AccountVerificationAPIView.as_view(), name="verify"),
]
