from django.urls import path

from ride.circles.views import list_circles

urlpatterns = [path("circles/", list_circles)]
