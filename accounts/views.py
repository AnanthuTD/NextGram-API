from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


@require_POST
def signup(request):
    data = json.loads(request.body)

    if data.email:
        email = data.email
        phone = None
    else:
        email = None
        phone = data.phone
    password = data.password
    name = data.name
    user_name = data.username

    response = JsonResponse({
        'email': True,
        'phone': True,
        'password': True,
        'name': True,
        'user_name': True
    })

    if User.objects.filter(email=email).exists():
        response.email = False
    if User.objects.filter(phone=phone).exists():
        response.phone = False
    if User.objects.filter(username=user_name).exists():
        response.user_name = False
    else:
        user = User.objects.create_user(
            email=email,
            phone=phone,
            password=password,
            name=name,
            username=user_name,
        )

    return JsonResponse({'status': 'success'})


@require_POST
def isValid(request):
    data = json.loads(request.body)

    email = data.email | None
    phone = data.phone | None
    password = data.password
    name = data.name
    user_name = data.username

    response = JsonResponse({
        'email': True,
        'phone': True,
        'password': True,
        'name': True,
        'user_name': True
    })

    try:
        validate_email(email)
        if User.objects.filter(email=email).exists():
            response.email = False
    except:
        pattern = r'^\d{10}$'
        match = re.match(pattern, phone)
        if match:
            if User.objects.filter(phone=phone).exists():
                response.phone = False
        else:
            response.email = False
            response.phone = False

    if not validate_password_strength(password):
        ValidationError(
            'Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.')
        response.password = False

    if not validate_username(user_name):
        ValidationError(
            'Invalid Instagram username - must be between 2 and 30 characters long and may only include letters, numbers, periods, and underscores.')
        response.user_name = False
    else:
        if User.objects.filter(username=user_name).exists():
            response.user_name = False

    if not user_name:
        response.user_name = False

    return response


def validate_password_strength(value):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])(?=.{8,}).*$'
    if not re.match(pattern, value):
        return False
    return True


def validate_username(value):
    pattern = r'^[a-zA-Z0-9_.]{2,30}$'
    if not re.match(pattern, value):
        return False
    return True


@require_POST
def login(request):
    data = json.loads(request.body)
    emil = data.email
    password = data.password
    return JsonResponse({'status': 'success'})
