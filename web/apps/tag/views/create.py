from apps.tag.services import tag_service
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View


class TagCreateView(LoginRequiredMixin, View):
    """
    View для создания тега. Этот класс обрабатывает два HTTP-метода: GET и POST.

    Метод GET возвращает страницу создания тега, а метод POST обрабатывает
    данные формы для создания нового тега.

    В случае успешного создания тега, пользователь перенаправляется на страницу списка тегов,
    и выводится сообщение об успешном создании. В случае ошибки валидации, пользователь
    перенаправляется обратно на страницу создания тега с соответствующим сообщением об ошибке.
    """

    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Возвращает страницу создания тега.

        Args:
            request (HttpRequest): объект запроса

        Returns:
            HttpResponse: страница создания тега
        """
        return render(request, "tag/create/tag_create.html")

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        """
        Обрабатывает форму создания тега.

        Получает данные из POST-запроса, валидирует их и, если данные корректны, создает новый тег.

        Если валидация прошла успешно:
            - выводит сообщение об успехе
            - перенаправляет на страницу со списком тегов

        Если валидация не прошла:
            - выводит сообщение об ошибке
            - перенаправляет обратно на страницу создания тега

        Args:
            request (HttpRequest): объект запроса

        Returns:
            HttpResponseRedirect: редирект на страницу со списком тегов или на страницу создания текущего тега
        """
        name = request.POST.get("tagName").strip()
        tag_type = request.POST.get("tagType").strip()
        channel_id = request.POST.get("telegramChannel").strip()
        tag_to_create = tag_service.TagData(name, tag_type, channel_id)
        service = tag_service.TagService()
        validation_result = service.create_tag(tag_to_create)

        if validation_result.is_success():
            messages.success(request, "Тег успешно создан")
            return redirect(reverse("tag-list"))
        else:
            messages.error(request, validation_result.error_message)
            return redirect(reverse("tag-add"))
