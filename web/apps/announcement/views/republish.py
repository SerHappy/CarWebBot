from .utils.form_handlers import form_data_handler
from .utils.form_handlers import media_handler
from .utils.form_handlers import tags_handler
from apps.announcement.models import Announcement
from apps.bot.views import delete_announcement_from_channel
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

import pytz


@login_required(login_url=settings.LOGIN_URL)
def republish_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    """Снимает объявление с публикации и ставит его в очередь на публикацию."""
    announcement = get_object_or_404(Announcement, pk=pk)
    if announcement.processing_status == Announcement.ProcessingStatus.PUBLISHED:
        delete_announcement_from_channel(announcement)

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

    keys = request.POST.keys()
    if set(keys) == {"datetime", "timezone"}:
        pass
    else:
        announcement, tag_ids = form_data_handler.handle_form_data(request, announcement)
        tags_handler.handle_tags(tag_ids, announcement)
    if request.POST.get("uploadIds"):
        media_handler.handle_media_files(request, announcement)

    announcement.processing_status = Announcement.ProcessingStatus.AWAITING_PUBLICATION
    announcement.save()
    return HttpResponse(status=200)
