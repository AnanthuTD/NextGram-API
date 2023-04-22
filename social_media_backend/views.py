from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def root(request):
    print("loged in")
    return JsonResponse({"status":"ok"})