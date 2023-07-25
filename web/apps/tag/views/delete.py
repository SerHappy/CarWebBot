from apps.bot.views import delete_announcement_from_subchannel
from apps.bot.views import edit_announcement_in_channel
from apps.tag.models import Tag
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


@login_required(login_url=settings.LOGIN_URL)
def delete_tag(request: HttpRequest, pk: int) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    tag_announcements = list(tag.announcements.all())
    old_channel_id = tag.channel_id

    tag_name = tag.name

    for announcement in tag_announcements:
        delete_announcement_from_subchannel(announcement, tag)

    tag.delete()

    for announcement in tag_announcements:
        announcement.refresh_from_db()
        edit_announcement_in_channel(announcement, {tag_name: old_channel_id})
    messages.success(request, "Тег успешно удален")
    return HttpResponse(status=200)
