from .forms import UserLoginForm
from .forms import UserRegisterForm
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render


def register_view(request: HttpRequest) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Remove password_confirmation from the form data
            cleaned_data = form.cleaned_data
            cleaned_data.pop("password_confirmation")

            # Create the new user
            User.objects.create_user(**cleaned_data)
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect("announcement-list")
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    logout(request)
    return redirect("login")
