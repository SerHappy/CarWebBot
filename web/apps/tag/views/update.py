from .utils.form_handlers import form_data
from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View


class TagUpdateView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        tag = Tag.objects.get(pk=pk)
        ctx = {"tag": tag}
        return render(request, "tag/edit/tag_edit.html", ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        return form_data.handle_form_data(request, Tag.objects.get(pk=pk))
