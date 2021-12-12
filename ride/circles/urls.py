# Django
from django.urls import path, include

# from ride.circles.views import list_circles, create_circle

# Django REST framework
from rest_framework.routers import DefaultRouter

# Views
from .views import circles as circle_views
from .views import memberships as membership_views

# urlpatterns = [
#     path("circles/", list_circles),
#     path("circles/create/",create_circle)
#     ]

router = DefaultRouter()
router.register(r"circles", circle_views.CircleViewSet, basename="circle")
router.register(
    r"circles/(?P<slug_name>[a-zA-Z0-9_-]+)/members",
    membership_views.MembershipViewSet,
    basename="membership",
)

urlpatterns = [path("", include(router.urls))]
