from apps.announcement.models import Announcement
from apps.bot.views import delete_announcement_from_channel
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

import os
import shutil


@login_required(login_url=settings.LOGIN_URL)
def takeoff_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    """Снимает объявление с публикации с id `pk`."""
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    return HttpResponse(status=200)


@login_required(login_url=settings.LOGIN_URL)
def delete_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаляет объявление из канала и базы данных с id `pk`."""
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    media = announcement.media.all()
    for m in media:
        m.file.delete()
        m.delete()

    media_folder = os.path.join(settings.MEDIA_ROOT, str(pk))
    if os.path.isdir(media_folder):
        shutil.rmtree(media_folder)
    announcement.delete()
    return HttpResponse(status=200)
