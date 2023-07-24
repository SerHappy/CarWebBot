from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse


@login_required(login_url=settings.LOGIN_URL)
def check_tag(request: HttpRequest) -> JsonResponse:
    tag_name = request.GET.get("tag_name", None)
    tag_id = request.GET.get("tag_id", None)
    if tag_id:
        data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exclude(pk=tag_id).exists()}
    else:
        data = {"is_taken": Tag.objects.filter(name__iexact=tag_name).exists()}
    return JsonResponse(data)
