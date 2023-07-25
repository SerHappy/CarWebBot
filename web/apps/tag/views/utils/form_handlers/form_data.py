from apps.tag.models import Tag
from django.contrib import messages
from django.http import HttpRequest
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


def handle_form_data(request, tag: Tag = None) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    name, tag_type, channel_id = _get_form_data(request)
    validation = _validate_form_data(name, tag_type, tag)
    if validation.get("error"):
        messages.error(request, validation.get("error"))
        return redirect(reverse("tag-edit", args=[tag.id]) if tag else reverse("tag-add"))
    if tag:
        _update_tag(tag, name, tag_type, channel_id)
        messages.success(request, "Тег успешно обновлен")
    else:
        _create_tag(name, tag_type, channel_id)
        messages.success(request, "Тег успешно создан")
    return redirect(reverse("tag-list"))


def _get_form_data(request: HttpRequest) -> tuple[str | None, str | None, str | None]:
    name = request.POST.get("tagName")
    tag_type = request.POST.get("tagType")
    channel_id = request.POST.get("telegramChannel")
    return name, tag_type, channel_id


def _validate_form_data(name: str, tag_type: str, tag: Tag = None) -> dict[str, str] | dict[str, bool]:
    max_length = Tag._meta.get_field("name").max_length
    if name is None:
        return {"error": "Название тега не указано"}
    if Tag.objects.filter(name=name).exclude(pk=tag.id if tag else None).exists():
        return {"error": "Тег с таким именем уже существует"}
    if tag_type is None:
        return {"error": "Тип тега не указан"}
    if len(name) < 1:
        return {"error": "Название тега слишком короткое"}
    if len(name) > max_length:
        return {"error": "Название тега слишком длинное"}
    return {"success": True}


def _update_tag(tag: Tag, name: str, tag_type: str, channel_id: str) -> None:
    tag.name = name
    tag.type = tag_type
    tag.channel_id = channel_id
    tag.save()


def _create_tag(name: str, tag_type: str, channel_id: str) -> None:
    Tag.objects.create(name=name, type=tag_type, channel_id=channel_id)
