import logging
from django.http import JsonResponse
from .forms import PostForm
from django.views.decorators.http import require_GET
from .models import Post
from django.db.models import F


def post(request):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            post = form.save()
            return JsonResponse({'status': True})
        else:
            print("posting errors : ", form.errors)
            return JsonResponse({'status': False})

    elif request.method == "GET":
        user = request.user

        try:
            posts = list(user.post_set.all().values("post_id",
                                                    'file',
                                                    'like',
                                                    'shares',
                                                    'caption',
                                                    'hash_tag',
                                                    'mentions',
                                                    'location',))
            return JsonResponse({'status': True, 'posts': posts})
        except Exception as e:
            logging.error(e, exc_info=True)
            return JsonResponse({'status': False, 'message': str(e)})

    else:
        return JsonResponse({'status': False})


@require_GET
def allPost(request):

    postsQuery = Post.objects.select_related(
        "user").annotate(username=F('user__username'))

    posts = list(postsQuery.values())

    print("all posts : ", posts)

    return JsonResponse({'status': True, 'posts': posts})
