from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from typing import Literal


class UserManager(BaseUserManager):
    def create_user(self, email, password=None) -> "User":
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user  # type: ignore

    def create_superuser(self, email, password=None) -> "User":
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email: str = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    is_active: bool = models.BooleanField(default=True)
    is_admin: bool = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None) -> Literal[True]:
        return True

    def has_module_perms(self, app_label) -> Literal[True]:
        return True

    @property
    def is_staff(self) -> bool:
        return self.is_admin
