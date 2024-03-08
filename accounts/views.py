
from uuid import UUID
import uuid
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
import json
from .forms import SignupForm
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from django.contrib.auth.models import User, AbstractBaseUser, AnonymousUser
from django.db.models import F
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import Profile
from django.db.models import Prefetch
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count


@require_POST
def signup(request):

    # Parse the JSON data from the request body
    data = json.loads(request.body)

    # Create a form instance and populate it with the data
    form = SignupForm(data)

    # Validate the form data
    if form.is_valid():
        try:
            # Save the user data
            form.save()

            phone_email_username = data["username"]
            password = data["password1"]

            authuser = authenticate(
                request, phone_email_username=phone_email_username, password=password)

            # Remove session data
            request.session.flush()

            # create new session
            request.session.create()

            # set current user session data
            login(request, authuser)

            response = JsonResponse({
                'status': True,
                'user': serialize_to_dict(authuser)})  # type: ignore

            id_user = authuser.profile.id_user  # type: ignore
            response.set_cookie('user', value=id_user,
                                expires=request.session.get_expiry_date(), samesite='Lax')

            # Return a JSON response with the user data
            return response
        except:
            # Server_error(database)
            return JsonResponse({
                'status': False,
                'errors': {"server_error": True},
            })

    else:
        # Return a JSON response with the form errors
        return JsonResponse({
            'status': False,
            'errors': form.errors,
        })


def login_view(request: HttpRequest):
    try:
        if (request.method == 'POST'):
            data = json.loads(request.body)

            if not data:
                return JsonResponse({'status': False, 'errors': {}})

            phone_email_username = data['phone_email_username']
            password = data['password1']

            user = authenticate(
                request, phone_email_username=phone_email_username, password=password)

            if not user:
                return JsonResponse({'status': False, 'errors': {}})

            # set current user session data
            if user is not None:
                login(request, user)

            response = JsonResponse({
                'status': True,
                'user': serialize_to_dict(user)})  # type: ignore

            id_user = user.profile.id_user  # type: ignore
            response.set_cookie('user', value=id_user,
                                expires=request.session.get_expiry_date(), samesite='Lax', domain='localhost')

            return response

        elif (request.method == 'GET'):
            if request.user.is_authenticated and request.user.profile:  # type: ignore
                return JsonResponse({
                    'status': True,
                    'user': serialize_to_dict(request.user)})  # type: ignore
            else:
                logout_view(request)
                return JsonResponse({'status': False})

        else:
            return JsonResponse({'status': False})
    except ObjectDoesNotExist:
        return JsonResponse({'status': False})

def serialize_to_dict(user: User):
    profile: Profile = user.profile  # type: ignore
    following_ids = list(profile.following.values_list('id_user', flat=True))
    followers_ids = list(profile.followers.values_list(  # type: ignore
        'id_user', flat=True))

    return {
        'id_user': profile.id_user,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': profile.phone or '',
        'bio': profile.bio or '',
        'location': profile.location or '',
        'gender': profile.gender,
        'website': profile.website,
        'profile_img': profile.profile_img.url,
        'followers': followers_ids,
        'following': following_ids,
        'post_count': profile.post_count,
    }


@require_GET
def logout_view(request: HttpRequest):
    logout(request)
    response = JsonResponse({'status': True})
    response.delete_cookie('user')
    return response


@require_POST
def profile(request: HttpRequest):
    profile: Profile = request.user.profile  # type: ignore

    data = json.loads(request.body)
    profile.bio = data['bio']  # type: ignore
    profile.gender = data['gender']  # type: ignore
    profile.website = data['website']  # type: ignore
    profile.save()
    return JsonResponse({'status': True})


def get_profile(request: HttpRequest, username: str):
    username_validator = UnicodeUsernameValidator()
    is_username = username_validator.__call__(username) is None
    is_uuid = is_valid_uuid(username)
    if is_uuid:
        user = User.objects.get(profile__id_user=username)
    elif is_username:
        user = User.objects.get(username=username)
    else:
        return JsonResponse({'status': False})

    profile: Profile = user.profile  # type: ignore
    following_ids = list(profile.following.values_list('id_user', flat=True))
    followers_ids = list(profile.followers.values_list(  # type: ignore
        'id_user', flat=True))

    profile_res = {'id_user': profile.id_user,
                   'username': user.username,
                   'first_name': user.first_name,
                   'last_name': user.last_name,
                   'bio': profile.bio or '',
                   'location': profile.location or '',
                   'website': profile.website,
                   'profile_img': profile.profile_img.url,
                   'followers': followers_ids,
                   'following': following_ids,
                   'post_count': profile.post_count, }

    return JsonResponse({'status': True, 'profile': profile_res})


def follow(request: HttpRequest):
    if request.method == 'PUT':
        data = json.loads(request.body)
        id_user = data['id_user']
        if (request.user.is_authenticated and id_user):

            profile = Profile.objects.get(id_user=id_user)
            request.user.profile.following.add(profile)
            response = {'status': True,
                        'user': serialize_to_dict(request.user)}
            return JsonResponse(response)

    return JsonResponse({'status': False})


@require_http_methods(['DELETE'])
def unfollow(request: HttpRequest, id_user: UUID):
    if request.method == 'DELETE':
        if (request.user.is_authenticated and id_user):
            profile = Profile.objects.get(id_user=id_user)
            request.user.profile.following.remove(profile)
            response = {'status': True,
                        'user': serialize_to_dict(request.user)}
            return JsonResponse(response)

    return JsonResponse({'status': False})


def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


@require_GET
def followers(request: HttpRequest):
    user = request.user
    profile: Profile = user.profile
    followers: Profile = profile.followers.all()
    response = []
    for follower in followers:
        dict = {
            'user_id': follower.user.id,
            'profile_img': follower.profile_img.url,
            'username': follower.username,
            'name': follower.firstname + ' ' + follower.lastname
        }
        response.append(dict)

    return JsonResponse({'followers': response})


@require_GET
def followings(request: HttpRequest):
    user = request.user
    profile: Profile = user.profile
    followings: Profile = profile.following.all()
    response = []
    for following in followings:
        dict = {
            'user_id': following.user_id,
            'profile_img': following.profile_img.url,
            'username': following.username,
            'name': following.firstname + ' ' + following.lastname
        }
        response.append(dict)

    return JsonResponse({'followings': response})


def sort_by_relevance(user):
    return user.interaction_count


def sort_by_popularity(followers):
    return len(followers)


def sort_by_freshness(user):
    return user.posts_count
    

def suggested(current_user: AbstractBaseUser | AnonymousUser | User, followers: Profile):
    common_users = current_user.profile.following.intersection(
        followers)
    return common_users


@require_GET
def search(request: HttpRequest):

    # print(request.user.profile.followings)
    query = request.GET.get('q', '')
    if query == '':
        return JsonResponse({'message': 'No search query provided'})
    matching_users = User.objects.filter(username__contains=query).exclude(
        id=request.user.id).prefetch_related(
        Prefetch('profile__followers'))

    response = []

    for user in matching_users:
        # follower_usernames = [follower.username for follower in user.profile.followers.all()]

        follower = {
            'user_id': user.id,
            'id_user': user.profile.id_user,
            'username': user.username, 
            'fullname': user.first_name + ' ' + user.last_name,
            'profile_img': user.profile.profile_img.url,
            'followed_by': list(suggested(request.user, user.profile.followers.all()).values('user_id', 'user__username')),
        }
        response.append(follower)
        # print(follower)

    response.sort(key=lambda user: (len(user['followed_by']), sort_by_popularity(
        user['followed_by'])), reverse=True)

    return JsonResponse({'users': response})


def user_interests(request):
    if request.method == 'GET':
        interests = list(request.user.profile.interests.values_list('name', flat=True))
        return JsonResponse({'interests': interests}) 
    elif request.method == 'POST':
        interests:list[str] = json.loads(request.body)['interests']
        
        print('interests: ', interests)
        
        for i in range(len(interests)):
            interests[i] = interests[i].lower()
        
        request.user.profile.interests.set(interests)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    
@api_view(['GET'])
def suggested_users(request):
    user_profile = request.user.profile  # Assuming authenticated user
    interests = user_profile.interests.all()  # Get interests of the current user
    user_city = user_profile.location  # Get city of the current user

    # Retrieve 'n' from query parameters or set a default value
    n = int(request.GET.get('n', 5))  # Default to 5 if 'n' not provided in query parameters

    # Include users who have posted the liked posts of the current user
    liked_posts_users = User.objects.filter(post__likes=request.user)
    liked_posts_profiles = Profile.objects.filter(user__in=liked_posts_users, interests__in=interests, location=user_city)[:n]

    suggested_profiles = liked_posts_profiles

    # Check if the number of suggested profiles is less than 5
    if suggested_profiles.count() < n:
        # Get profiles of users who share at least one interest with the current user and are from the same location
        interest_location_profiles = Profile.objects.filter(interests__in=interests, location=user_city) \
            .exclude(user=request.user)[:n - suggested_profiles.count()]
        suggested_profiles = suggested_profiles | interest_location_profiles 

    # Check if the number of suggested profiles is still less than 5
    if suggested_profiles.count() < n:
        # Get profiles of users who share at least one interest with the current user
        interest_profiles = Profile.objects.filter(interests__in=interests) \
            .exclude(user=request.user)[:n - suggested_profiles.count()]
        suggested_profiles = suggested_profiles | interest_profiles

    # Check if the number of suggested profiles is still less than 5
    if suggested_profiles.count() < n:
        # Get profiles of users from the same location
        location_profiles = Profile.objects.filter(location=user_city) \
            .exclude(user=request.user)[:n - suggested_profiles.count()]
        suggested_profiles = suggested_profiles | location_profiles

    # Get profiles of users with the most followers
    most_followed_profiles = Profile.objects.annotate(num_followers=Count('followers')).order_by('-num_followers')[:n - suggested_profiles.count()]
    suggested_profiles = suggested_profiles | most_followed_profiles

    # Ensure the final suggested profiles queryset contains only unique profiles
    suggested_profiles = suggested_profiles.distinct()

    # Serialize data
    suggested_users_data = [{'username': profile.username,
                             'id': profile.user_id}
                            for profile in suggested_profiles]

    return Response({'suggested_users': suggested_users_data})

