from django.core.validators import validate_email
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()


class SignupForm(UserCreationForm):
    phone_or_email = forms.CharField(max_length=100, required=True)
    id_user = forms.IntegerField()
    bio = forms.CharField(max_length=500, required=False)
    profile_img = forms.ImageField(required=False)
    location = forms.CharField(max_length=100, required=False)
    email = None
    phone = None

    class Meta:
        model = User
        fields = ('username', 'password1', 'email')

    def clean_phone_or_email(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')
        if not phone_or_email:
            raise forms.ValidationError('Phone or email is required')
        elif phone_or_email.isdigit():
            pattern = r'^\d{10}$'
            match = re.match(pattern, phone_or_email)
            if not match:
                raise forms.ValidationError('Invalid phone number')
            if Profile.objects.filter(phone=phone_or_email).exists():
                raise forms.ValidationError('Phone number already exists')
            self.phone = phone_or_email
        else:
            if not validate_email(phone_or_email):
                raise forms.ValidationError('Invalid email address')
            if User.objects.filter(email=phone_or_email).exists():
                raise forms.ValidationError('Email address already exists')
            self.email = phone_or_email
        return phone_or_email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.email:
            user.email = self.email
        user.save()
        profile = Profile.objects.create(user=user)
        if self.phone:
            profile.phone = self.phone
        if self.cleaned_data.get('id_user'):
            profile.id_user = self.cleaned_data['id_user']
        if self.cleaned_data.get('bio'):
            profile.bio = self.cleaned_data['bio']
        if self.cleaned_data.get('profile_img'):
            profile.profile_img = self.cleaned_data['profile_img']
        if self.cleaned_data.get('location'):
            profile.location = self.cleaned_data['location']
        profile.save()
        return user
