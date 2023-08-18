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


class TagUpdateView(LoginRequiredMixin, View):
    """
    View для обновления тега. Этот класс обрабатывает два HTTP-метода: GET и POST.

    Метод GET возвращает страницу обновления тега, а метод POST обрабатывает
    данные формы для обновления тега.

    В случае успешного обновления тега, пользователь перенаправляется на страницу списка тегов,
    и выводится сообщение об успешном обновлении. В случае ошибки валидации, пользователь
    перенаправляется обратно на страницу обновления тега с соответствующим сообщением об ошибке.
    """

    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest, pk: int) -> HttpResponse | HttpResponseRedirect:
        """
        Возвращает страницу обновления тега.

        Args:
            request (HttpRequest): объект запроса
            pk (int): ID тега

        Returns:
            HttpResponse | HttpResponseRedirect:
            страница обновления тега или редирект на страницу со списком тегов и сообщением об отсутствии тега
        """
        service = tag_service.TagService()
        tag_to_update = service.fetch_tag_from_db(pk)
        if not tag_to_update:
            messages.error(request, "Тег не найден")
            return redirect(reverse("tag-list"))
        ctx = {"tag": tag_to_update}
        return render(request, "tag/edit/tag_edit.html", ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponseRedirect:
        """
        Обрабатывает форму обновления тега.

        Получает данные из POST-запроса, валидирует их и, если данные корректны, обновляет тег с переданным id.

        Если валидация прошла успешно:
            - выводит сообщение об успехе
            - перенаправляет на страницу со списком тегов

        Если валидация не прошла:
            - выводит сообщение об ошибке
            - перенаправляет обратно на страницу обновления тега

        Args:
            request (HttpRequest): объект запроса
            pk (int): ID тега

        Returns:
            HttpResponseRedirect: редирект на страницу со списком тегов или на страницу обновления текущего тега
        """
        name = request.POST.get("tagName").strip()
        tag_type = request.POST.get("tagType").strip()
        channel_id = request.POST.get("telegramChannel").strip()
        tag_to_update = tag_service.TagData(name, tag_type, channel_id, pk)
        service = tag_service.TagService()
        validation_result = service.update_tag(tag_to_update)

        if validation_result.is_success():
            messages.success(request, "Тег успешно обновлен")
            return redirect(reverse("tag-list"))
        else:
            messages.error(request, validation_result.error_message)
            return redirect(reverse("tag-edit", args=[pk]))
