import traceback
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import json
from django.core import serializers
from .forms import SignupForm
from django.contrib.auth import authenticate, login


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
            user = form.save()

            phone_email_username = data["username"]
            password = data["password1"]

            newuser = authenticate(
            request, phone_email_username=phone_email_username, password=password)
           
            # Remove session data
            request.session.flush()

            # create new session
            request.session.create()
          
            # set current user session data
            try:
                login(request, newuser)
            except Exception as e:
                print("error logging in")
                traceback.print_exc()
                raise ValueError("intentional")

            # Return a JSON response with the user data
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
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


def loginView(request):
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

        # # set current user session data
        if user is not None:
            login(request, user)

        return JsonResponse({
            'status': True,
            'user': serialize_to_dict(user)})

    elif (request.method == 'GET'):
        if request.user.is_authenticated:
            return JsonResponse({
                'status': True,
                'user': serialize_to_dict(request.user)})
        return JsonResponse({'status': False})

    else:
        return JsonResponse({'status': False})


def serialize_to_dict(user):
    return {
        # 'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.profile.phone or '',
        'bio': user.profile.bio or '',
        'location': user.profile.location or '',
    }
