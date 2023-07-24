from apps.announcement.models import Announcement
from apps.announcement.models import Media
from apps.bot.views import delete_announcement_from_channel
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

import mimetypes
import os
import pytz
import shutil


tmp_storage = FileSystemStorage(location=settings.TMP_STORAGE_PATH)


@login_required(login_url=settings.LOGIN_URL)
def republish_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    if announcement.is_published:
        delete_announcement_from_channel(announcement)

    keys = request.POST.keys()
    if set(keys) == {"datetime", "timezone"}:
        new_date = request.POST.get("datetime")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(new_date, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)
        if date_with_tz < datetime.now(pytz_timezone):
            now = datetime.now(pytz_timezone)
            date_with_tz = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

        date_utc = date_with_tz.astimezone(pytz.UTC)
        announcement.publication_date = date_utc
    else:
        name = request.POST.get("name")
        text = request.POST.get("text")
        tag_str = request.POST.get("tags")
        tag_ids = sorted(tag_str.split(",") if tag_str else [])
        price = request.POST.get("price")
        status = request.POST.get("status")
        note = request.POST.get("note", None)

        announcement = Announcement.objects.get(pk=pk)
        announcement.name = name
        announcement.text = text
        announcement.price = price
        announcement.status = status
        announcement.note = note
        announcement.save()

        announcement.tags.set(tag_ids)
        new_date = request.POST.get("datetime")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(new_date, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)

        if date_with_tz < datetime.now(pytz_timezone):
            now = datetime.now(pytz_timezone)
            date_with_tz = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

        date_utc = date_with_tz.astimezone(pytz.UTC)

        announcement.publication_date = date_utc
        upload_ids_string = request.POST.getlist("uploadIds")[0]
        upload_ids = upload_ids_string.split(",")

        existing_files = [media.file.name for media in announcement.media.all()]
        for file_name in existing_files:
            if file_name not in upload_ids:
                media = Media.objects.get(file=file_name, announcement=announcement)
                media.file.delete()
                media.delete()

        for index, upload_id in enumerate(upload_ids):
            tmp_dir = tmp_storage.path(upload_id)
            if os.path.exists(tmp_dir):
                for filename in os.listdir(tmp_dir):
                    file_path = f"{upload_id}/{filename}"
                    file = tmp_storage.open(file_path)
                    content_type, encoding = mimetypes.guess_type(file_path)
                    media_type = Media.MediaType.PHOTO if "image" in content_type else Media.MediaType.VIDEO
                    new_media = Media.objects.create(
                        media_type=media_type,
                        file=file,
                        announcement=announcement,
                        order=index,
                    )
                    file.close()
                    upload_ids[index] = new_media.file.name
                shutil.rmtree(tmp_dir)

        for index, upload_id in enumerate(upload_ids):
            try:
                media = Media.objects.get(file=upload_id, announcement=announcement)
                media.order = index
                media.save()
            except Media.DoesNotExist:
                pass

    announcement.processing_status = Announcement.ProcessingStatus.PENDING
    announcement.is_published = False
    announcement.is_active = True
    announcement.save()
    return HttpResponse(status=200)
