from .models import Tag
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import View
from loguru import logger
from typing import Any
from typing import Dict


@login_required(login_url="/user/login/")
def check_tag(request: HttpRequest) -> JsonResponse:
    tag_name = request.GET.get("tag_name", None)
    data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exists()}
    return JsonResponse(data)


class TagCreation(LoginRequiredMixin, View):
    login_url = "/users/login/"

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

        paginator = Paginator(context["tags"], 1)
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
        return render(request, "tag/tag_edit.html", ctx)
