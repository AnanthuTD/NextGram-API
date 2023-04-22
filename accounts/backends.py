import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.models import User, Profile
logger = logging.getLogger(__name__)


class UsernameEmailPhoneBackend(ModelBackend):
    def authenticate(self, request, phone_email_username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(Q(username=phone_email_username) | Q(
                email=phone_email_username) | Q(profile__phone=phone_email_username))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except user_model.DoesNotExist:
            return None
