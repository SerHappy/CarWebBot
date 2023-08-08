from .models import User
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from django.contrib.auth import authenticate
from django.contrib.auth import login
from loguru import logger


class ServiceResult(ABC):
    def __init__(self, is_success: bool, message: str) -> None:
        self.is_success = is_success
        self.message = message

    def is_successful(self) -> bool:
        return self.is_success

    @abstractmethod
    def successful() -> "ServiceResult":
        pass

    @abstractmethod
    def failure(error_message: str) -> "ServiceResult":
        return ServiceResult(False, error_message)


class RegistrationResult(ServiceResult):
    @staticmethod
    def successful() -> "RegistrationResult":
        return RegistrationResult(True, "User registered successfully.")

    @staticmethod
    def failure(error_message: str) -> "RegistrationResult":
        return RegistrationResult(False, error_message)


class LoginResult(ServiceResult):
    @staticmethod
    def successful() -> "LoginResult":
        return LoginResult(True, "User logged in successfully.")

    @staticmethod
    def failure(error_message: str) -> "LoginResult":
        return LoginResult(False, error_message)


@dataclass
class UserData:
    email: str
    password: str


class RegistrationService:
    def register(self, user_data: UserData) -> RegistrationResult:
        try:
            User.objects.create_user(email=user_data.email, password=user_data.password)
            return RegistrationResult.successful()
        except Exception as e:
            logger.error(f"Unhandled exception in user registration: {e}. Fix this ASAP!")
            return RegistrationResult.failure(
                "Something went wrong. Please try again later. If the problem persists, contact the administrator."
            )


class LoginService:
    def login(self, request, user_data: UserData) -> LoginResult:
        user = authenticate(request, username=user_data.email, password=user_data.password)
        if user is not None:
            login(request, user)
            return LoginResult.successful()
        else:
            return LoginResult.failure("Invalid credentials.")
