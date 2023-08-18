from .models import Setting
from django import forms


class SettingsForm(forms.ModelForm):
    """Класс формы настроек."""

    unpublish_date = forms.DateTimeField(
        input_formats=["%d.%m.%Y %H:%M"],
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control datetimepicker-input",
                "data-target": "#reservationdatetime",
                "id": "unpublish_date",
            }
        ),
    )

    class Meta:
        """Мета-класс для формы настроек."""

        model = Setting
        fields = ["unpublish_date"]
