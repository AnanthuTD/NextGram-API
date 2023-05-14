
from uuid import UUID
import uuid
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
import json
from .forms import SignupForm
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from django.contrib.auth.models import User
from django.db.models import F
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import Profile


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