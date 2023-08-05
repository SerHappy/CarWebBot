from django.conf import settings
from django.core.files.storage import FileSystemStorage


tmp_storage = FileSystemStorage(location=settings.TMP_STORAGE_PATH)
