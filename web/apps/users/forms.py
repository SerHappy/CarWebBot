from .models import User
from django import forms
from typing import Any


class UserRegisterForm(forms.ModelForm):
    """Форма регистрации пользователя."""

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )

    class Meta:
        """Мета-класс для формы регистрации пользователя."""

        model = User
        fields = ["email", "password"]

    def clean(self) -> dict[str, Any]:
        """Очищает данные формы и проверяет пароли на совпадение."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password != password_confirmation:
            self.add_error("password_confirmation", "Passwords must match")

        return cleaned_data


class UserLoginForm(forms.Form):
    """Форма входа пользователя."""

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))
