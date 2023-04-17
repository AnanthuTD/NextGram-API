from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import QueryDict
import json

@require_POST
def signup(request):
    data = json.loads(request.body)
    emil = data.email
    password = data.password
    return JsonResponse({'status' : 'success'})

@require_POST
def login(request):
    data = json.loads(request.body)
    emil = data.email
    password = data.password
    return JsonResponse({'status' : 'success'})