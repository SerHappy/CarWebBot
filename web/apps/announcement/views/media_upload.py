from ..storage import tmp_storage
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.generic import View
from loguru import logger
from urllib.parse import unquote

import os
import shutil
import uuid


class MediaUploadView(View):
    """Класс для загрузки медиа."""

    def post(self, request: HttpRequest) -> JsonResponse:
        """Ендпоинт для загрузки медиа на сервер через Dropzone."""
        files = list(request.FILES.values())
        upload_ids = []

        for file in files:
            file.name = file.name.lower()

            upload_id = str(uuid.uuid4())
            filename = f"{file.name}"
            tmp_storage.save(f"{upload_id}/{filename}", file)
            upload_ids.append(upload_id)

        return JsonResponse({"uploadId": upload_id})

    def delete(self, request: HttpRequest, upload_id: str) -> JsonResponse:
        """Ендпоинт для удаления медиа с сервера."""
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
