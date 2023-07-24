from .utils.form_handlers import form_data_handler
from .utils.form_handlers import media_handler
from .utils.form_handlers import tags_handler
from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View


class AnnouncementCreateView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        action_url = reverse("announcement-add")
        ctx = {
            "action": action_url,
            "tags": tags,
            "announcement": "null",
        }
        return render(request, "announcement/create/announcement_create.html", ctx)

    def post(self, request: HttpRequest) -> HttpResponse:
        announcement, tags = form_data_handler.handle_form_data(request)
        media_handler.handle_media_files(request, announcement)
        tags_handler.handle_tags(tags, announcement)
        return redirect("announcement-list")
