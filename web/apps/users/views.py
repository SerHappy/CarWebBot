from .forms import UserLoginForm
from .forms import UserRegisterForm
from .services import LoginService
from .services import RegistrationService
from .services import UserData
from django.contrib import messages
from django.contrib.auth import logout
from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from typing import Any


class RegisterView(FormView):
    """Класс для регистрации пользователя."""

    template_name = "register/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")

    def post(self, request: HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        """Обработка POST-запроса."""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            error_message = "Form is not valid: " + ", ".join([str(err) for err in form.errors])
            messages.error(request, error_message)
            return self.form_invalid(form)

    def form_valid(self, form: Form) -> HttpResponse:
        """Валидация формы."""
        cleaned_data = form.cleaned_data
        cleaned_data.pop("password_confirmation")
        user_to_register = UserData(**cleaned_data)
        service = RegistrationService()
        result = service.register(user_to_register)
        if result.is_successful():
            messages.success(self.request, result.message)
            return super().form_valid(form)
        else:
            messages.error(self.request, result.message)
            return redirect("register")


class LoginView(FormView):
    """Класс для входа пользователя."""

    template_name = "login/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("announcement-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        """Обработка GET-запроса."""
        if request.user.is_authenticated:
            return redirect("announcement-list")
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        """Обработка POST-запроса."""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            error_message = "Form is not valid: " + ", ".join([str(err) for err in form.errors])
            messages.error(request, error_message)
            return self.form_invalid(form)

    def form_valid(self, form: Form) -> HttpResponse | None:
        """Валидация формы."""
        user_to_login = UserData(**form.cleaned_data)
        service = LoginService()
        result = service.login(self.request, user_to_login)
        if result.is_successful():
            messages.success(self.request, result.message)
            return super().form_valid(form)
        else:
            messages.error(self.request, result.message)
            return redirect("login")


class LogoutView(RedirectView):
    """Класс для выхода пользователя."""

    url = reverse_lazy("login")

    def get(self, request: HttpRequest, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        """Обработка GET-запроса."""
        logout(request)
        return super().get(request, *args, **kwargs)
