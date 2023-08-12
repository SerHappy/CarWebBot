from .views import SettingsFormView
from django.urls import path


urlpatterns = [
    path("", SettingsFormView.as_view(), name="settings"),
]
