from apps.tag.services import tag_service
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import HttpResponse
from django.views.generic import View


class TagDeleteView(LoginRequiredMixin, View):
    """
    Класс для удаления тега.

    Этот класс обрабатывает только DELETE метод.
    """

    login_url = settings.LOGIN_URL

    def delete(self, request: HttpRequest, pk: int) -> HttpResponse:
        """
        Удаляет тег по его id.

        Args:
            request (HttpRequest): объект запроса
            pk (int): id тега

        Returns:
            HttpResponse: ответ с кодом 200, если тег успешно удален, иначе 400
        """
        service = tag_service.TagService()
        delete_result = service.delete_tag(pk)
        if delete_result.is_success():
            messages.success(request, "Тег успешно удален")
            return HttpResponse(status=200)
        else:
            messages.error(request, delete_result.message)
        return HttpResponse(status=400)
