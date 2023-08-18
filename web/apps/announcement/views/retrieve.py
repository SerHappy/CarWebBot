from apps.announcement.models import Announcement
from apps.announcement.services import get_status
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


@login_required(login_url=settings.LOGIN_URL)
def get_announcement_status(request: HttpRequest, pk: int) -> JsonResponse:
    """Ендпоинт для получения статуса объявления."""
    announcement = get_object_or_404(Announcement, pk=pk)
    status = get_status(announcement)
    publication_date = announcement.publication_date
    unpublished_date = announcement.unpublished_date
    published_message_link = announcement.published_message_link
    return JsonResponse(
        {
            "status": status,
            "publication_date": publication_date,
            "unpublished_date": unpublished_date,
            "published_message_link": published_message_link,
        }
    )
