from apps.bot.views import delete_announcement_from_channel
from apps.bot.views import edit_announcement_in_channel
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.generic import View
from loguru import logger
from urllib.parse import unquote

import os
import shutil
import uuid


tmp_storage = FileSystemStorage(location=settings.TMP_STORAGE_PATH)


class MediaUploadView(View):
    def post(self, request) -> JsonResponse:
        files = list(request.FILES.values())
        upload_ids = []

        for file in files:
            file.name = file.name.lower()

            upload_id = str(uuid.uuid4())
            filename = f"{file.name}"
            tmp_storage.save(f"{upload_id}/{filename}", file)
            upload_ids.append(upload_id)

        return JsonResponse({"uploadId": upload_id})

    def delete(self, request, upload_id) -> JsonResponse:
        upload_id = unquote(upload_id)
        if "/" in upload_id:
            return JsonResponse(
                {
                    "status": 200,
                    "text": "This file is already in announcement and will be delete after sending form",
                },
            )
        folder_path = os.path.join(tmp_storage.location, upload_id)

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")

        os.rmdir(folder_path)

        return JsonResponse(
            {
                "status": 200,
            }
        )
