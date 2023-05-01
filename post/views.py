from django.http import JsonResponse
from .forms import PostForm
from django.views.decorators.csrf import csrf_exempt

def post(request):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            post = form.save()
            return JsonResponse({'status':True})
        else:
            print("posting errors : ",form.errors)
            return JsonResponse({'status':False})
    else:
        return JsonResponse({'status':False})
    
