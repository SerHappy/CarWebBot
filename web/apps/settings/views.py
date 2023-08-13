from .forms import SettingsForm
from .models import Setting
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

import pytz


class SettingsFormView(LoginRequiredMixin, FormView):
    login_url = settings.LOGIN_URL
    template_name = "settings/settings.html"
    form_class = SettingsForm
    success_url = reverse_lazy("settings")

    def get(self, request, *args, **kwargs):
        settings = Setting.objects.first()
        form = self.form_class(instance=settings)

        if settings and settings.unpublish_date:
            unpublish_date_utc = settings.unpublish_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            unpublish_date_utc = None

        return self.render_to_response(self.get_context_data(form=form, unpublish_date_utc=unpublish_date_utc))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            if form.cleaned_data["unpublish_date"] is None:
                Setting.objects.update_or_create(id=1, defaults={"unpublish_date": None})
                messages.success(request, "Дата сброшена. Настройки успешно сохранены")
                return redirect(self.success_url)

            unpublish_date_row = form.cleaned_data["unpublish_date"]
            naive_date = unpublish_date_row.replace(tzinfo=None)
            timezone = request.POST.get("timezone")
            user_timezone = pytz.timezone(timezone)
            localized_date = user_timezone.localize(naive_date)
            date_in_utc = localized_date.astimezone(pytz.UTC)

            Setting.objects.update_or_create(id=1, defaults={"unpublish_date": date_in_utc})
            messages.success(request, "Дата установлена. Настройки успешно сохранены")
            return redirect(self.success_url)
        return self.form_invalid(form)
