from apps.announcement.models import Announcement
from apps.announcement.models import Media
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest

import mimetypes
import os
import shutil


tmp_storage = FileSystemStorage(location=settings.TMP_STORAGE_PATH)


def handle_media_files(request: HttpRequest, announcement: Announcement) -> None:
    upload_ids = _get_upload_ids_from_request(request)
    if announcement.is_published:
        _delete_media_files(upload_ids, announcement)
    _add_new_media_files(upload_ids, announcement)
    if announcement.is_published:
        _update_existing_media_files_order(upload_ids, announcement)


def _get_upload_ids_from_request(request: HttpRequest) -> list[str]:
    return request.POST.getlist("uploadIds")[0].split(",")


def _add_new_media_files(upload_ids: list[str], announcement: Announcement) -> None:
    for index, upload_id in enumerate(upload_ids):
        tmp_dir = tmp_storage.path(upload_id)
        if os.path.exists(tmp_dir):
            for filename in os.listdir(tmp_dir):
                file_path = f"{upload_id}/{filename}"
                file = tmp_storage.open(file_path)
                content_type, encoding = mimetypes.guess_type(file_path)
                media_type = Media.MediaType.PHOTO if "image" in content_type else Media.MediaType.VIDEO
                Media.objects.create(
                    media_type=media_type,
                    file=file,
                    announcement=announcement,
                    order=index,
                )
                file.close()

            shutil.rmtree(tmp_dir)


def _update_existing_media_files_order(upload_ids: list[str], announcement: Announcement) -> None:
    for index, upload_id in enumerate(upload_ids):
        try:
            media = Media.objects.get(file=upload_id, announcement=announcement)
            media.order = index
            media.save()
        except Media.DoesNotExist:
            pass


def _delete_media_files(upload_ids: list[str], announcement: Announcement) -> None:
    existing_files = [media.file.name for media in announcement.media.all()]
    for file_name in existing_files:
        if file_name not in upload_ids:
            media = Media.objects.get(file=file_name, announcement=announcement)
            media.file.delete()
            media.delete()
