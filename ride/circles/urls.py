# Django
from django.urls import path, include
from rest_framework import routers

# from ride.circles.views import list_circles, create_circle

# Django REST framework
from rest_framework.routers import DefaultRouter

# Views
from .views import circles as circle_views

# urlpatterns = [
#     path("circles/", list_circles),
#     path("circles/create/",create_circle)
#     ]

router = DefaultRouter()
router.register(r'circles', circle_views.CircleViewSet, basename='circle')

urlpatterns = [
    path('', include(router.urls))
]
