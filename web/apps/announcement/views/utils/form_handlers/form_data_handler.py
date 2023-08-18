from apps.announcement.models import Announcement
from datetime import datetime
from datetime import timedelta
from django.http import HttpRequest

import pytz


def handle_form_data(request: HttpRequest, announcement: Announcement = None) -> tuple[Announcement, list[str]]:
    """
    Обрабатывает данные формы.

    Args:
        request (HttpRequest): Запрос.

        announcement (Announcement, optional): Объявление. По умолчанию None.

    Returns:
        tuple[Announcement, list[str]]: Объявление и список его тегов.
    """
    name = request.POST.get("name")
    text = request.POST.get("text")
    tag_str = request.POST.get("tags")
    tag_ids = sorted(tag_str.split(",") if tag_str else [])
    price = request.POST.get("price")
    status = request.POST.get("status")
    note = request.POST.get("note")

    if announcement:
        announcement.name = name
        announcement.text = text
        announcement.price = price
        announcement.status = status
        announcement.note = note
        announcement.save()
    else:
        publication_date_row = request.POST.get("publication_date")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(publication_date_row, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)

        if date_with_tz < datetime.now(pytz_timezone):
            now = datetime.now(pytz_timezone)
            date_with_tz = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

        date_utc = date_with_tz.astimezone(pytz.UTC)

        announcement = Announcement.objects.create(
            name=name,
            text=text,
            price=price,
            status=status,
            note=note,
            publication_date=date_utc,
        )

    return announcement, tag_ids
