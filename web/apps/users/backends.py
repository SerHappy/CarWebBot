from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from typing import Any


class EmailBackend(ModelBackend):
    """Класс для аутентификации пользователя по email."""

    def authenticate(
        self,
        request: HttpRequest,
        username: str | None = None,
        password: str | None = None,
        **kwargs: dict[str, Any],
    ) -> AbstractBaseUser | None:
        """Аутентифицирует пользователя по email."""
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        """Получает пользователя по id."""
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
