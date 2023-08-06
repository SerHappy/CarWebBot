from apps.announcement.models import Announcement
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Case
from django.db.models import IntegerField
from django.db.models import Value
from django.db.models import When
from django.views.generic import ListView
from loguru import logger
from typing import Any


class AnnouncementListView(LoginRequiredMixin, ListView):
    login_url = settings.LOGIN_URL
    model = Announcement
    template_name = "announcement/announcement_list.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["announcements"] = Announcement.objects.annotate(
            custom_order=Case(
                When(is_active=True, is_published=False, processing_status="P", then=Value(1)),
                When(is_active=True, is_published=True, processing_status="D", then=Value(2)),
                When(is_active=False, is_published=False, processing_status="P", then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by("custom_order", "-publication_date", "-id")
        name_filter = self.request.GET.get("nameFilter")
        tag_filter = self.request.GET.get("tagFilter")
        if name_filter:
            context["announcements"] = context["announcements"].filter(name__icontains=name_filter)
        if tag_filter:
            context["announcements"] = context["announcements"].filter(tags__name__icontains=tag_filter)

        paginator = Paginator(context["announcements"], settings.ANNOUNCEMENT_LIST_PER_PAGE)
        page = self.request.GET.get("page")
        try:
            context["announcements"] = paginator.page(page)
            logger.info(f"Page number: {page}")
        except PageNotAnInteger:
            logger.info("Page number not an integer")
            context["announcements"] = paginator.page(1)
            logger.info("Page number: 1")
        except EmptyPage:
            logger.info("Page number empty")
            context["announcements"] = paginator.page(paginator.num_pages)
            logger.info("Page number: ", paginator.num_pages)
        logger.debug(f"Returned context: {context}"[:100])

        return context
