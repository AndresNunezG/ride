from django.http import HttpResponse, JsonResponse

from ride.circles.models import Circle


def list_circles(request):
    public_circle = Circle.objects.filter(is_public=True)
    data = []
    for circle in public_circle:
        print("hola")
    return HttpResponse("Hola")
