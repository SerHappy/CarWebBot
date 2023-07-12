from .models import Tag
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from loguru import logger


@login_required(login_url="/user/login/")
def check_tag(request: HttpRequest) -> JsonResponse:
    tag_name = request.GET.get("tag_name", None)
    data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exists()}
    return JsonResponse(data)


class TagCreation(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"tags": tags}
        return render(request, "tag/create/tag_create.html", ctx)

    def post(self, request: HttpRequest) -> JsonResponse:
        name = request.POST.get("tagName")
        type = request.POST.get("tagType")
        channel_id = request.POST.get("telegramChannel")
        max_length = Tag._meta.get_field("name").max_length

        if len(name) < 1:
            logger.error("Tag could not be created, because name is too short")
            return JsonResponse({"status": "error", "message": "Название тега слишком короткое"})

        if len(name) > max_length:
            logger.error("Tag could not be created, because name is too long")
            return JsonResponse({"status": "error", "message": "Название тега слишком длинное"})

        tag, created = Tag.objects.get_or_create(name=name, type=type, channel_id=channel_id)
        if created:
            logger.info(f"Tag created: {tag}")
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Тег успешно создан",
                    "id": tag.id,
                    "name": tag.name,
                    "type": tag.type,
                    "channel_id": tag.channel_id,
                }
            )
        else:
            logger.error("Tag could not be created, because one already exists")
            return JsonResponse({"status": "error", "message": "Такой тег уже существует"})


class TagListView(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"tags": tags}
        return render(request, "tag/tag_list.html", ctx)
