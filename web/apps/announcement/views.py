from ..tag.models import Tag
from .models import Announcement
from .models import Media
from .serializers import serialize_media
from .services import get_status
from apps.bot.views import delete_announcement_from_channel
from apps.bot.views import edit_announcement_in_channel
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
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
from urllib.parse import unquote

import mimetypes
import os
import pytz
import shutil
import uuid


@login_required(login_url="/users/login/")
def takeoff_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    return HttpResponse(status=200)


@login_required(login_url="/users/login/")
def delete_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    delete_announcement_from_channel(announcement)
    media = announcement.media.all()
    for m in media:
        m.file.delete()
        m.delete()

    media_folder = os.path.join(settings.MEDIA_ROOT, str(pk))
    if os.path.isdir(media_folder):
        shutil.rmtree(media_folder)
    announcement.delete()
    return HttpResponse(status=200)


@login_required(login_url="/users/login/")
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


@login_required(login_url="/users/login/")
def get_announcement_status(request: HttpRequest, pk: int) -> JsonResponse:
    announcement = get_object_or_404(Announcement, pk=pk)
    status = get_status(announcement)
    publication_date = announcement.publication_date
    return JsonResponse({"status": status, "publication_date": publication_date})


tmp_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR, "tmp"))


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


class AnnouncementListView(LoginRequiredMixin, ListView):
    login_url = "/users/login/"
    model = Announcement
    template_name = "announcement/announcement_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["announcements"] = Announcement.objects.all()
        name_filter = self.request.GET.get("nameFilter")
        tag_filter = self.request.GET.get("tagFilter")
        if name_filter:
            context["announcements"] = context["announcements"].filter(name__icontains=name_filter)
        if tag_filter:
            context["announcements"] = context["announcements"].filter(tags__name__icontains=tag_filter)

        paginator = Paginator(context["announcements"], 5)
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
    login_url = "/users/login/"

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"action": f"/announcements/add/", "tags": tags, "announcement": "null"}
        return render(request, "announcement/create/announcement_create.html", ctx)

    def post(self, request: HttpRequest) -> HttpResponse:
        name = request.POST.get("name")
        text = request.POST.get("text")
        tag_str = request.POST.get("tags")
        tag_ids = sorted(tag_str.split(",") if tag_str else [])
        price = request.POST.get("price")
        status = request.POST.get("status")
        note = request.POST.get("note", None)
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
        announcement.tags.set(tag_ids)

        upload_ids_string = request.POST.getlist("uploadIds")[0]
        upload_ids = upload_ids_string.split(",")
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

        return redirect("announcement-list")


class AnnouncementUpdate(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        announcement = Announcement.objects.get(pk=pk)
        announcement_json = serialize("json", [announcement])
        announcement_tags = announcement.tags.all()
        announcement_media = announcement.media.all().order_by("order")

        valid_announcement_media = []
        missing_files = []

        for media in announcement_media:
            if os.path.isfile(media.file.path):
                valid_announcement_media.append(media)
            else:
                missing_files.append(media.file.name)
                media.delete()

        for i, media in enumerate(valid_announcement_media):
            media.order = i
            media.save()

        media_json = serialize_media(valid_announcement_media)

        all_tags = Tag.objects.all()
        ctx = {
            "action": f"/announcements/edit/{announcement.pk}/",
            "announcement_id": announcement.pk,
            "announcement": announcement_json,
            "announcement_tags": announcement_tags,
            "tags": all_tags,
            "media": media_json,
            "missing_files": missing_files,
        }

        return render(request, "announcement/edit/announcement_edit.html", ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
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

        old_tags = {tag: tag.channel_id for tag in announcement.tags.all()}

        announcement.tags.set(tag_ids)

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
        if announcement.is_published:
            edit_announcement_in_channel(announcement, old_tags)

        return redirect("announcement-list")
