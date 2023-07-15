from .models import Tag
from apps.bot.views import delete_announcement_from_subchannel
from apps.bot.views import edit_announcement_in_channel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic import View
from loguru import logger
from typing import Any
from typing import Dict


@login_required(login_url="/users/login/")
def check_tag(request: HttpRequest) -> JsonResponse:
    tag_name = request.GET.get("tag_name", None)
    tag_id = request.GET.get("tag_id", None)
    if tag_id:
        data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exclude(pk=tag_id).exists()}
    else:
        data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exists()}
    return JsonResponse(data)


@login_required(login_url="/users/login/")
def delete_tag(request: HttpRequest, pk: int) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    tag_announcements = list(tag.announcements.all())
    old_channel_id = tag.channel_id  # Запоминаем старый channel_id

    for announcement in tag_announcements:
        delete_announcement_from_subchannel(announcement, tag)

    tag.delete()

    for announcement in tag_announcements:
        announcement.refresh_from_db()
        edit_announcement_in_channel(announcement, {tag: old_channel_id})
    return HttpResponse(status=200)


class TagCreateView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"tags": tags}
        return render(request, "tag/create/tag_create.html", ctx)

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        name = request.POST.get("tagName", None)
        type = request.POST.get("tagType", None)
        channel_id = request.POST.get("telegramChannel", None)
        max_length = Tag._meta.get_field("name").max_length

        existing_tag = Tag.objects.filter(name=name).first()
        if existing_tag:
            messages.error(request, "Тег с таким именем уже существует")
            return HttpResponseRedirect(reverse("tag-add"))

        if len(name) < 1:
            messages.error(request, "Название тега слишком короткое")
            return HttpResponseRedirect(reverse("tag-add"))

        if len(name) > max_length:
            messages.error(request, "Название тега слишком длинное")
            return HttpResponseRedirect(reverse("tag-add"))

        try:
            Tag.objects.create(name=name, type=type, channel_id=channel_id)
            messages.success(request, "Тег успешно создан")
            return HttpResponseRedirect(reverse("tag-list"))
        except Tag.DoesNotExist:
            messages.error(request, "Тег не существует")
            return HttpResponseRedirect(reverse("tag-add"))


class TagListView(LoginRequiredMixin, ListView):
    login_url = "/users/login/"
    model = Tag
    template_name = "tag/tag_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        name_filter = self.request.GET.get("nameFilter", None)
        if name_filter:
            context["tags"] = context["tags"].filter(name__icontains=name_filter)

        paginator = Paginator(context["tags"], 10)
        page = self.request.GET.get("page")
        try:
            context["tags"] = paginator.page(page)
            logger.info(f"Page {page} of tags was loaded")
        except (PageNotAnInteger, ValueError):
            logger.warning(f"Page {page} of tags was not an integer")
            context["tags"] = paginator.page(1)
            logger.info(f"Page 1 of tags was loaded")
        except EmptyPage:
            logger.warning(f"Page {page} of tags was empty")
            context["tags"] = paginator.page(paginator.num_pages)
            logger.info(f"Last page of tags was loaded")
        except InvalidPage:
            logger.warning(f"Page {page} of tags was invalid")
            context["tags"] = paginator.page(1)
            logger.info(f"Page 1 of tags was loaded")
        return context


class TagEditView(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        tag = Tag.objects.get(pk=pk)
        ctx = {"tag": tag}
        return render(request, "tag/edit/tag_edit.html", ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        name = request.POST.get("tagName")
        type = request.POST.get("tagType")
        channel_id = request.POST.get("telegramChannel")
        max_length = Tag._meta.get_field("name").max_length

        existing_tag = Tag.objects.filter(name=name).exclude(pk=pk).first()
        if existing_tag:
            messages.error(request, "Тег с таким именем уже существует")
            return HttpResponseRedirect(reverse("tag-edit", args=[pk]))

        if len(name) < 1:
            messages.error(request, "Название тега слишком короткое")
            return HttpResponseRedirect(reverse("tag-edit", args=[pk]))

        if len(name) > max_length:
            messages.error(request, "Название тега слишком длинное")
            return HttpResponseRedirect(reverse("tag-edit", args=[pk]))

        try:
            tag = Tag.objects.get(pk=pk)
            old_channel_id = tag.channel_id  # Запоминаем старый channel_id
            tag.name = name
            tag.type = type
            tag.channel_id = channel_id
            tag.save()
            messages.success(request, "Тег успешно обновлен")
        except Tag.DoesNotExist:
            messages.error(request, "Тег не существует")
            return HttpResponseRedirect(reverse("tag-edit", args=[pk]))

        for announcement in tag.announcements.all():
            edit_announcement_in_channel(announcement, {tag: old_channel_id})
        return HttpResponseRedirect(reverse("tag-list"))
