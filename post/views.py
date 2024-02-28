import json
import logging
from pprint import pprint
from uuid import UUID
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from .forms import PostForm, StoryForm
from django.views.decorators.http import require_GET, require_http_methods
from .models import Post, Story, User, Comment
from django.db.models import F, Prefetch
from accounts.models import Profile


def post(request: HttpRequest, other_user=None):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        else:
            print("posting errors : ", form.errors)
            return JsonResponse({'status': False})

    elif request.method == "GET":
        if other_user:
            user = get_object_or_404(User, username=other_user)
        else:
            user = request.user
        try:
            posts = list(user.post_set.all().values("id",
                                                    'file',
                                                    'likes',
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

    # pprint(posts)

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
    post = get_object_or_404(Post, id=post_id)

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


def comments(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            comment = data.get("comment")

            if not comment or not isinstance(comment, str):
                return JsonResponse({'status': False, 'message': 'Invalid comment format'})

            post_id = data.get('id')
            print('postid ', data)
            post = get_object_or_404(Post, id=post_id)

            comment_instance = Comment.objects.create(
                post=post, author=request.user, comment=comment)

            serialized_comment = serializers.serialize('json', [comment_instance])
            return JsonResponse({'status': True, 'message': 'Comment created', 'comment': serialized_comment})

        except json.JSONDecodeError:
            return JsonResponse({'status': False, 'message': 'Invalid JSON format'})
        except Post.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Post does not exist'})

    elif request.method == 'GET':
        try:            
            post_id = request.GET.get('id')
            print('post_id')
            post = get_object_or_404(Post, id=post_id)
            comments = Comment.objects.filter(post=post).select_related('author')
            serialized_comments = serializers.serialize('json', comments)
            return JsonResponse({'status': True, 'comments': serialized_comments})
        except Post.DoesNotExist:
            print('nothing')
            return JsonResponse({'status': False, 'message': 'Post does not exist'})

    else:
        return JsonResponse({'status': False, 'message': 'Invalid request method'})


def story(request: HttpRequest):

    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES, user_id=request.user.id)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        else:
            print("posting errors : ", form.errors)
            return JsonResponse({'status': False})
    else:
        return JsonResponse({'status': False})


@require_GET
def stories(request: HttpRequest):
    profile = Profile.objects.prefetch_related(Prefetch("following")).get(user=request.user)
    # pprint(profile.following.values())
    following_list = profile.following.all()
    stories = Story.objects.filter(user__profile__in=following_list).select_related('user')
    # print('stories = ', stories)
    
    stories_dict = {}

    for story in stories:
        # print('story', story.user.id)
        user = story.user
        
        if user.id in stories_dict:
            stories_dict[user.id]['stories'].append({'story':story.file.url, 'story_id': story.id})
            # print('story_dict = ', stories_dict)
        else:
            stories_dict[user.id] = {
                'user_id': user.id,
                'username': user.get_username(),
                'profile_img': story.user.profile.profile_img.url,
                'stories': [{'story':story.file.url, 'story_id': story.id}],
                'caption': story.caption,
                'hash_tag': story.hash_tag,
                'mentions': story.mentions,
                'location': story.location
            }
            
        # print(stories_dict)
        
    # storiesList = list(stories_dict.values())
    # print('storiesList', str(stories_dict.values()))
    return JsonResponse({'status': True, 'stories': list(stories_dict.values())})


