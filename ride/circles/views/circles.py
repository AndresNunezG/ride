# Django REST Framework
from rest_framework import viewsets

# Serializers
from ride.circles.serializers import CircleModelSerializer

# Models
from ride.circles.models import Circle

class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer