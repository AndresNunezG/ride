from django.http import HttpResponse, JsonResponse

from ride.circles.models import Circle


def list_circles(request):
    public_circle = Circle.objects.filter(is_public=True)
    data = []
    for circle in public_circle:
        data.append({
            'name': circle.name,
            'slug_name': circle.slug_name,
            'verified': circle.verified,
        })
    return JsonResponse(data, safe=False)
 