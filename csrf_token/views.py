from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET

@require_GET
def get_csrf_token(request):
    request.session.flush()

    request.session.create()

    token = get_token(request)
    
    return JsonResponse({'csrfToken': token})
