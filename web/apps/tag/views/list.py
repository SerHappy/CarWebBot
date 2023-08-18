from apps.tag.models import Tag
from apps.tag.services import tag_service
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from typing import Any


class TagListView(LoginRequiredMixin, ListView):
    """Класс для отображения списка тегов."""

    login_url = settings.LOGIN_URL
    model = Tag
    template_name = "tag/tag_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Получает контекст данных для отображения списка тегов. Применяет фильтрацию и пагинацию, если необходимо.

        Args:
            **kwargs: Дополнительные аргументы для контекста.

        Returns:
            dict[str, Any]: Словарь с контекстом для отображения списка тегов.
        """
        service = tag_service.TagService()
        context = super().get_context_data(**kwargs)
        name_filter = self.request.GET.get("nameFilter")
        page_number = self.request.GET.get("page", 1)
        context["tags"] = service.get_tags_for_display(
            name_filter=name_filter,
            page=page_number,
            page_size=settings.TAG_LIST_PER_PAGE,
        )
        return context
