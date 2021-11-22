from django.urls import path

from ride.circles.views import list_circles, create_circle

urlpatterns = [path("circles/", list_circles), path("circles/create/", create_circle)]
