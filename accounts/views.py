from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.core import serializers
# from accounts.backends import PhoneBackend
from .forms import SignupForm
from django.contrib.auth import authenticate


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


@require_POST
def login(request):
    data = json.loads(request.body)

    if not data:
        return JsonResponse({'status': False, 'errors': {}})

    phone_email_username = data['phone_email_username']
    password = data['password']

    user = authenticate(
        request, phone_email_username=phone_email_username, password=password)
    
    if not user:
        return JsonResponse({'status': False, 'errors': {}})

    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.profile.phone,
            'bio': user.profile.bio,
            'location': user.profile.location,
        }})
