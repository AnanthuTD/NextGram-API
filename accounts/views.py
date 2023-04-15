from django.http import HttpResponse, JsonResponse

# Create your views here.

def signup(request):
    if(request.method == 'POST'):
        return JsonResponse({"status":"ok"})