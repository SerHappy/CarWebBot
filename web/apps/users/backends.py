from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser


class EmailBackend(ModelBackend):
    """Класс для аутентификации пользователя по email."""

    def authenticate(self, request, username=None, password=None, **kwargs) -> AbstractBaseUser | None:
        """Аутентифицирует пользователя по email."""
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id) -> AbstractBaseUser | None:
        """Получает пользователя по id."""
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
