from .utils.form_handlers import form_data_handler
from .utils.form_handlers import media_handler
from .utils.form_handlers import tags_handler
from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.announcement.serializers import serialize_media
from apps.bot.views import edit_announcement_in_channel
from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View

import os


class AnnouncementUpdateView(LoginRequiredMixin, View):
    """Класс для обработки запроса на редактирование объявления."""

    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Обработка GET запроса на редактирование объявления."""
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement_tags = announcement.tags.all()
        announcement_media = announcement.media.all().order_by("order")

        valid_announcement_media, missing_files = self._validate_and_clean_media(announcement_media)
        self._update_media_order(valid_announcement_media)

        all_tags = Tag.objects.all()
        ctx = {
            "action": reverse("announcement-edit", args=[announcement.pk]),
            "announcement_id": announcement.pk,
            "announcement": serialize("json", [announcement]),
            "announcement_tags": announcement_tags,
            "tags": all_tags,
            "media": serialize_media(valid_announcement_media),
            "missing_files": missing_files,
        }

        return render(request, "announcement/edit/announcement_edit.html", ctx)

    def _validate_and_clean_media(self, media_list: list[Media]) -> tuple[list[Media], list[str]]:
        valid_media = []
        missing_files = []

        for media in media_list:
            if os.path.isfile(media.file.path):
                valid_media.append(media)
            else:
                missing_files.append(media.file.name)
                media.delete()
        return valid_media, missing_files

    def _update_media_order(self, media_list: list[Media]) -> None:
        for i, media in enumerate(media_list):
            media.order = i
            media.save()

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Обработка POST запроса на редактирование объявления."""
        announcement = Announcement.objects.get(pk=pk)
        announcement, tag_ids = form_data_handler.handle_form_data(request, announcement)

        old_tags = {tag: tag.channel_id for tag in announcement.tags.all()}
        tags_handler.handle_tags(tag_ids, announcement)

        media_handler.handle_media_files(request, announcement)

        if announcement.is_published:
            edit_announcement_in_channel(announcement, old_tags)

        return redirect("announcement-list")
