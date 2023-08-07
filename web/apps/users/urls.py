from .views import LoginView
from .views import LogoutView
from .views import RegisterView
from django.conf import settings
from django.urls import path


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
if settings.DEBUG:
    urlpatterns += path("register/", RegisterView.as_view(), name="register")
