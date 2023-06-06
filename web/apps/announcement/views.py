from .models import Announcement
from .models import Media
from .models import Tag
from .services import get_status
from apps.bot.tasks import publish_announcements
from apps.bot.views import delete_announcement_from_channel
from apps.bot.views import edit_announcement_in_channel
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import View
from loguru import logger

import pytz


@login_required(login_url="/user/login/")
def takeoff_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    return HttpResponse(status=200)


@login_required(login_url="/user/login/")
def delete_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    media = announcement.media.all()
    for m in media:
        m.file.delete()
        m.delete()
    announcement.delete()
    return HttpResponse(status=200)


@login_required(login_url="/user/login/")
def republish_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    if announcement.is_published:
        delete_announcement_from_channel(announcement)

    keys = request.POST.keys()
    # If only datetime and timezone are passed, handle only them
    if set(keys) == {"datetime", "timezone"}:
        new_date = request.POST.get("datetime")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(new_date, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)
        date_utc = date_with_tz.astimezone(pytz.UTC)
        announcement.publication_date = date_utc
    else:
        name = request.POST.get("name")
        text = request.POST.get("text")
        tags = request.POST.getlist("tags")
        if tags == [""]:
            tags = []
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

        announcement.tags.set(tags)
        new_date = request.POST.get("datetime")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(new_date, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)
        date_utc = date_with_tz.astimezone(pytz.UTC)
        announcement.publication_date = date_utc
        # Handle existing media files
        existing_files = request.POST.get("existing_files").split(",") if request.POST.get("existing_files") else []
        current_files = [media.file.name for media in announcement.media.all()]

        for file_name in current_files:
            if file_name not in existing_files:
                media = Media.objects.get(file=file_name, announcement=announcement)
                media.file.delete()
                media.delete()

        # Handle new media files
        for file in request.FILES.getlist("media"):
            content_type = file.content_type.split("/")[0]
            media_type = Media.MediaType.PHOTO if content_type == "image" else Media.MediaType.VIDEO
            Media.objects.create(media_type=media_type, file=file, announcement=announcement)

    announcement.processing_status = Announcement.ProcessingStatus.PENDING
    announcement.is_published = False
    announcement.is_active = True
    announcement.save()
    return HttpResponse(status=200)


@login_required(login_url="/user/login/")
def get_announcement_status(request: HttpRequest, pk: int) -> JsonResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    status = get_status(announcement)
    publication_date = announcement.publication_date
    return JsonResponse({"status": status, "publication_date": publication_date})


class AnnouncementListView(LoginRequiredMixin, ListView):
    login_url = "/user/login/"
    model = Announcement
    template_name = "index.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["announcements"] = Announcement.objects.all()
        name_filter = self.request.GET.get("nameFilter")
        tag_filter = self.request.GET.get("tagFilter")
        if name_filter:
            context["announcements"] = context["announcements"].filter(name__icontains=name_filter)
        if tag_filter:
            context["announcements"] = context["announcements"].filter(tags__name__icontains=tag_filter)

        paginator = Paginator(context["announcements"], self.paginate_by)
        page = self.request.GET.get("page")
        try:
            context["announcements"] = paginator.page(page)
            logger.info(f"Page number: {page}")
        except PageNotAnInteger:
            logger.info("Page number not an integer")
            context["announcements"] = paginator.page(1)
            logger.info("Page number: 1")
        except EmptyPage:
            logger.info("Page number empty")
            context["announcements"] = paginator.page(paginator.num_pages)
            logger.info("Page number: ", paginator.num_pages)
        logger.debug(f"Returned context: {context}"[:100])

        return context


class AnnouncementCreation(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"action": f"/announcements/add/", "tags": tags, "announcement": "null"}
        return render(request, "announcement/announcement_form.html", ctx)

    def post(self, request: HttpRequest) -> HttpResponse:
        name = request.POST.get("name")
        text = request.POST.get("text")
        tags = request.POST.getlist("tags")
        price = request.POST.get("price")
        status = request.POST.get("status")
        note = request.POST.get("note", None)
        publication_date_row = request.POST.get("publication_date")
        timezone = request.POST.get("timezone")
        pytz_timezone = pytz.timezone(timezone)
        date_format = "%d.%m.%Y %H:%M"
        date_without_tz = datetime.strptime(publication_date_row, date_format)
        date_with_tz = pytz_timezone.localize(date_without_tz)
        date_utc = date_with_tz.astimezone(pytz.UTC)
        announcement = Announcement.objects.create(
            name=name,
            text=text,
            price=price,
            status=status,
            note=note,
            publication_date=date_utc,
        )
        announcement.tags.set(tags)

        for file in request.FILES.getlist("media"):
            content_type = file.content_type.split("/")[0]
            media_type = Media.MediaType.PHOTO if content_type == "image" else Media.MediaType.VIDEO
            Media.objects.create(media_type=media_type, file=file, announcement=announcement)

        return redirect("announcement-list")


class AnnouncementUpdate(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        announcement = Announcement.objects.get(pk=pk)
        announcement_json = serialize("json", [announcement])
        announcement_tags = announcement.tags.all()
        announcement_media = announcement.media.all()
        media_json = serialize("json", announcement_media)
        all_tags = Tag.objects.all()
        ctx = {
            "action": f"/announcements/edit/{announcement.pk}/",
            "announcement_id": announcement.pk,
            "announcement": announcement_json,
            "announcement_tags": announcement_tags,
            "tags": all_tags,
            "media": media_json,
        }

        return render(request, "announcement/announcement_update.html", ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        name = request.POST.get("name")
        text = request.POST.get("text")
        tags = request.POST.getlist("tags")
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

        announcement.tags.set(tags)

        # Handle existing media files
        existing_files = request.POST.get("existing_files").split(",") if request.POST.get("existing_files") else []
        current_files = [media.file.name for media in announcement.media.all()]

        for file_name in current_files:
            if file_name not in existing_files:
                media = Media.objects.get(file=file_name, announcement=announcement)
                media.file.delete()
                media.delete()

        # Handle new media files
        for file in request.FILES.getlist("media"):
            content_type = file.content_type.split("/")[0]
            media_type = Media.MediaType.PHOTO if content_type == "image" else Media.MediaType.VIDEO
            Media.objects.create(media_type=media_type, file=file, announcement=announcement)

        edit_announcement_in_channel(announcement)

        return redirect("announcement-list")


class TagCreation(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def post(self, request) -> JsonResponse:
        name = request.POST.get("tagName")

        max_length = Tag._meta.get_field("name").max_length

        if len(name) < 1:
            logger.error("Tag could not be created, because name is too short")
            return JsonResponse({"status": "error", "message": "Название тега слишком короткое"})

        if len(name) > max_length:
            logger.error("Tag could not be created, because name is too long")
            return JsonResponse({"status": "error", "message": "Название тега слишком длинное"})

        tag, created = Tag.objects.get_or_create(name=name)
        if created:
            logger.info(f"Tag created: {tag}")
            return JsonResponse({"status": "success", "message": "Тег успешно создан", "id": tag.id, "name": tag.name})
        else:
            logger.error("Tag could not be created, because one already exists")
            return JsonResponse({"status": "error", "message": "Такой тег уже существует"})
