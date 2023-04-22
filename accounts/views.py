from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers
# from accounts.backends import PhoneBackend
from .forms import SignupForm
from django.contrib.auth import authenticate, login as set_login


@require_POST
def signup(request):

    # Parse the JSON data from the request body
    data = json.loads(request.body)
    print(data)

    # Create a form instance and populate it with the data
    form = SignupForm(data)

    # Validate the form data
    if form.is_valid():
        try:
            # Save the user data
            user = form.save()

            # Remove session data
            request.session.flush()

            # create new session
            request.session.create()

            # Return a JSON response with the user data
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email or "",
                    'phone': form.phone or "",
                    # 'id_user': form.cleaned_data['id_user'],
                    'bio': form.cleaned_data.get('bio', ''),
                    'location': form.cleaned_data.get('location', ''),
                }})
        except:
            # Server_error(database)
            return JsonResponse({
                'success': False,
                'errors': {"server_error": True},
            })

    else:
        # Return a JSON response with the form errors
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        })


def login(request):
    if (request.method == 'POST'):
        data = json.loads(request.body)

        if not data:
            return JsonResponse({'status': False, 'errors': {}})

        phone_email_username = data['phone_email_username']
        password = data['password']

        user = authenticate(
            request, phone_email_username=phone_email_username, password=password)

        if not user:
            return JsonResponse({'status': False, 'errors': {}})

        set_login(request, user)

        return JsonResponse({
            'status': True,
            'user': serialize_to_dict(user)})

    elif (request.method == 'GET'):
        if request.user.is_authenticated:
            return JsonResponse({
                'status': True,
                'user': serialize_to_dict(request.user)})
        return JsonResponse({'status': False})


def serialize_to_dict(user):
    return {
        # 'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.profile.phone or '',
        'bio': user.profile.bio or '',
        'location': user.profile.location or '',
    }
