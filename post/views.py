import logging
from pprint import pprint
from uuid import UUID
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from .forms import PostForm
from django.views.decorators.http import require_GET, require_http_methods
from .models import Post, User
from django.db.models import F, Prefetch


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
def allPost(request: HttpRequest):
    postsQuery = Post.objects.prefetch_related(Prefetch("likes", queryset=User.objects.only(
        "username", "first_name", "last_name"))).select_related('user').exclude(user=request.user)

    posts = []

    for post in postsQuery:
        # Create a new dictionary for the updated post
        new_post = {}

        # Copy over all the attributes from the original post
        for key, value in vars(post).items():
            if key not in ('_prefetched_objects_cache', '_state'):
                new_post[key] = value

        # Add the new 'likes' field to the new post
        new_post['likes'] = likes_serializer(post.likes)

        new_post['username'] = post.user.get_username()

        # Add the new post to the list
        posts.append(new_post)

    pprint(posts)

    return JsonResponse({'status': True, 'posts': posts})


@ require_http_methods(['PATCH'])
def like(request, post_id: UUID):
    # Make sure the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('You must be logged in to like a post.')

    # Get the post object or return a 404 error if it doesn't exist
    post = get_object_or_404(Post, pk=post_id)

    # Add the user to the post's likes
    post.likes.add(request.user)

    post.save()

    # Return a success JSON response
    data = {'success': True, 'message': 'Post liked successfully.',
            'likes': likes_serializer(post.likes)}

    return JsonResponse(data)


@ require_http_methods(['PATCH'])
def dislike(request, post_id: UUID):
    # Make sure the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('You must be logged in to like a post.')

    # Get the post object or return a 404 error if it doesn't exist
    post = get_object_or_404(Post, pk=post_id)

    # Add the user to the post's likes
    try:
        post.likes.remove(request.user)
        post.save()
    except:
        pass

    # Return a success JSON response
    data = {'success': True, 'message': 'Post liked successfully.', 'likes': likes_serializer(post.likes)
            }
    return JsonResponse(data)


def likes_serializer(likes):
    return list(likes.annotate(
        profile_img=F('profile__profile_img'), id_user=F('profile__id_user')
    ).values(
        "username",
        "first_name",
        "last_name",
        "profile_img",
        "id_user"
    ))
