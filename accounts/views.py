from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def signup(request):
    return JsonResponse({"status":"ok"})