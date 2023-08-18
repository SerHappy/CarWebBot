from .models import User
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from django.contrib.auth import authenticate
from django.contrib.auth import login
from loguru import logger


class ServiceResult(ABC):
    """Базовый класс для результатов работы сервисов."""

    def __init__(self, is_success: bool, message: str) -> None:
        """Конструктор класса."""
        self.is_success = is_success
        self.message = message

    def is_successful(self) -> bool:
        """Возвращает True, если результат работы сервиса успешен, иначе False."""
        return self.is_success

    @abstractmethod
    def successful(self) -> "ServiceResult":
        """Возвращает успешный результат работы сервиса."""
        pass

    @abstractmethod
    def failure(self, error_message: str) -> "ServiceResult":
        """Возвращает неуспешный результат работы сервиса."""
        pass


class RegistrationResult(ServiceResult):
    """Класс для результатов регистрации пользователя."""

    @staticmethod
    def successful() -> "RegistrationResult":
        """Возвращает успешный результат регистрации пользователя."""
        return RegistrationResult(True, "User registered successfully.")

    @staticmethod
    def failure(error_message: str) -> "RegistrationResult":
        """Возвращает неуспешный результат регистрации пользователя."""
        return RegistrationResult(False, error_message)


class LoginResult(ServiceResult):
    """Класс для результатов входа пользователя."""

    @staticmethod
    def successful() -> "LoginResult":
        """Возвращает успешный результат входа пользователя."""
        return LoginResult(True, "User logged in successfully.")

    @staticmethod
    def failure(error_message: str) -> "LoginResult":
        """Возвращает неуспешный результат входа пользователя."""
        return LoginResult(False, error_message)


@dataclass
class UserData:
    """Дата-класс для данных пользователя."""

    email: str
    password: str


class RegistrationService:
    """Класс для регистрации пользователя."""

    def register(self, user_data: UserData) -> RegistrationResult:
        """Регистрирует пользователя и возвращает результат регистрации."""
        try:
            User.objects.create_user(email=user_data.email, password=user_data.password)
            return RegistrationResult.successful()
        except Exception as e:
            logger.error(f"Unhandled exception in user registration: {e}. Fix this ASAP!")
            return RegistrationResult.failure(
                "Something went wrong. Please try again later. If the problem persists, contact the administrator."
            )


class LoginService:
    """Класс для входа пользователя."""

    def login(self, request, user_data: UserData) -> LoginResult:
        """Логинит пользователя и возвращает результат входа."""
        user = authenticate(request, username=user_data.email, password=user_data.password)
        if user is not None:
            login(request, user)
            return LoginResult.successful()
        else:
            return LoginResult.failure("Invalid credentials.")
