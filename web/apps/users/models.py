from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from typing import Any
from typing import Literal


class UserManager(BaseUserManager):
    """Класс для управления моделью `User`."""

    def create_user(self, email: str, password: str | None = None) -> "User":
        """Создает и возвращает пользователя с указанными email и паролем."""
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None) -> "User":
        """Создает и возвращает суперпользователя с указанными email и паролем."""
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Модель пользователя."""

    email: str = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    is_active: bool = models.BooleanField(default=True)
    is_admin: bool = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        """Мета-класс для модели пользователя."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """Строковое представление модели пользователя."""
        return self.email

    def has_perm(self, perm: Any, obj: Any | None = None) -> Literal[True]:
        """Проверяет, имеет ли пользователь указанный набор прав."""
        return True

    def has_module_perms(self, app_label: Any) -> Literal[True]:
        """Проверяет, имеет ли пользователь права на доступ к приложению `app_label`."""
        return True

    @property
    def is_staff(self) -> bool:
        """Проверяет, является ли пользователь администратором."""
        return self.is_admin
