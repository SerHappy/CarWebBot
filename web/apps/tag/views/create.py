from .utils.form_handlers import form_data
from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View


class TagCreateView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest) -> HttpResponse:
        tags = Tag.objects.all()
        ctx = {"tags": tags}
        return render(request, "tag/create/tag_create.html", ctx)

    def post(self, request: HttpRequest) -> HttpResponseRedirect | JsonResponse:
        return form_data.handle_form_data(request)
