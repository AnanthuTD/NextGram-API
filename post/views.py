from django.http import JsonResponse
from .forms import PostForm
from django.views.decorators.csrf import csrf_exempt

def post(request):
    file = request.FILES
    caption = request.POST.get('caption')
    location = request.POST.get('location')

    print('user : ',request.user.id)

    print(file, caption, location)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            post = form.save()
            return JsonResponse({'status':True})
        else:
            print(form.errors)
            return JsonResponse({'status':False})
    else:
        return JsonResponse({'status':False})
    
