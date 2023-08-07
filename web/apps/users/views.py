from .forms import UserLoginForm
from .forms import UserRegisterForm
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView


class RegisterView(FormView):
    template_name = "register/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form) -> HttpResponse:
        cleaned_data = form.cleaned_data
        cleaned_data.pop("password_confirmation")
        User.objects.create_user(**cleaned_data)
        return super().form_valid(form)


class LoginView(FormView):
    template_name = "login/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("announcement-list")

    def get(self, request, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("announcement-list")
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse | None:
        user = authenticate(self.request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return redirect("login")


class LogoutView(RedirectView):
    url = reverse_lazy("login")

    def get(self, request, *args, **kwargs) -> HttpResponse:
        logout(request)
        return super().get(request, *args, **kwargs)
