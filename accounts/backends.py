import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser

from models import Profile
from accounts.models import User

logger = logging.getLogger(__name__)

class PhoneBackend(BaseBackend):
    def authenticate(self, request, phone: str | None = ..., password: str | None = ...) -> AbstractBaseUser | None:
        logger.debug('Attempting authentication for phone: %s', phone)
        try:
            user = Profile.objects.get(phone=phone)
            print(user);
        except Profile.DoesNotExist:
            return None
        return user
