from apps.announcement.models import Announcement
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import Page
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Value
from django.db.models import When
from django.views.generic import ListView
from loguru import logger
from typing import Any


class AnnouncementListView(LoginRequiredMixin, ListView):
    """Список объявлений."""

    login_url = settings.LOGIN_URL
    model = Announcement
    template_name = "announcement/announcement_list.html"

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """Получение контекста для шаблона."""
        context = super().get_context_data(**kwargs)
        context["announcements"] = Announcement.objects.annotate(
            custom_order=Case(
                When(Q(processing_status="AWAITING") | Q(processing_status="PROCESSING"), then=Value(1)),
                When(processing_status="PUBLISHED", then=Value(2)),
                When(Q(processing_status="UNPUBLISHED") | Q(processing_status="INACTIVE"), then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by("custom_order", "-publication_date", "-id")
        name_filter = self.request.GET.get("nameFilter")
        tag_filter = self.request.GET.get("tagFilter")
        status_filter = self.request.GET.get("statusFilter")
        context["announcements"] = self._filter_announcements(
            announcements=context["announcements"],
            name_filter=name_filter,
            tag_filter=tag_filter,
            status_filter=status_filter,
        )
        context["announcements"] = self._paginate_announcements(announcements=context["announcements"])

        return context

    def _filter_announcements(
        self,
        announcements: QuerySet[Announcement],
        name_filter: str | None,
        tag_filter: str | None,
        status_filter: str | None,
    ) -> QuerySet[Announcement]:
        """
        Фильтрация объявлений.

        Args:
            announcements (QuerySet[Announcement]): QuerySet объявлений.

            name_filter (str, optional): Фильтр по названию объявления.

            tag_filter (str, optional): Фильтр по тегу объявления.

            status_filter (str, optional): Фильтр по статусу объявления.

        Returns:
            QuerySet[Announcement]: Отфильтрованный QuerySet объявлений.
        """
        if name_filter:
            announcements = announcements.filter(name__icontains=name_filter)
        if tag_filter:
            announcements = announcements.filter(tags__name__icontains=tag_filter)
        if status_filter:
            if status_filter == "all":
                pass
            elif status_filter == "takenoff":
                announcements = announcements.filter(
                    Q(processing_status="UNPUBLISHED") | Q(processing_status="INACTIVE")
                )
            elif status_filter == "published":
                announcements = announcements.filter(processing_status="PUBLISHED")
            elif status_filter == "waiting":
                announcements = announcements.filter(
                    Q(processing_status="AWAITING") | Q(processing_status="PROCESSING")
                )
        return announcements

    def _paginate_announcements(self, announcements: QuerySet[Announcement]) -> Page:
        """
        Пагинирует объявления.

        Args:
            announcements (QuerySet[Announcement]): QuerySet объявлений.

        Returns:
            Page: Объект страницы, содержащий объявления.
        """
        paginator = Paginator(announcements, settings.ANNOUNCEMENT_LIST_PER_PAGE)
        page = self.request.GET.get("page")
        try:
            logger.info(f"Page number: {page}")
            return paginator.page(page)
        except PageNotAnInteger:
            logger.info("Page number not an integer")
            logger.info("Page number: 1")
            return paginator.page(1)
        except EmptyPage:
            logger.info("Page number empty")
            logger.info("Page number: ", paginator.num_pages)
            return paginator.page(paginator.num_pages)
