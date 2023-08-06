from apps.tag.services import tag_service
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http import JsonResponse
from django.views import View


class TagCheckView(LoginRequiredMixin, View):
    """View для проверки, существует ли тег с таким именем в базе данных. Этот класс обрабатывает только GET метод"""

    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Получает имя тега и проверяет, существует ли он в базе данных.
        Если передан id тега, то исключает его из проверки.

        Args:
            request (HttpRequest): объект запроса

        Returns:
            JsonResponse:
            JSON-объект с ключом is_taken, который содержит True, если тег с таким именем существует, иначе False
        """
        tag_name = request.GET.get("tag_name", None)
        tag_id = request.GET.get("tag_id", None)
        validator = tag_service.TagValidator()
        is_tag_taken = validator.check_is_tag_name_taken(tag_name, tag_id)
        return JsonResponse({"is_taken": is_tag_taken})
