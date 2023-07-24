from apps.announcement.models import Announcement
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.views.generic import ListView
from loguru import logger
from typing import Any


class AnnouncementListView(LoginRequiredMixin, ListView):
    login_url = settings.LOGIN_URL
    model = Announcement
    template_name = "announcement/announcement_list.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["announcements"] = Announcement.objects.all()
        name_filter = self.request.GET.get("nameFilter")
        tag_filter = self.request.GET.get("tagFilter")
        if name_filter:
            context["announcements"] = context["announcements"].filter(name__icontains=name_filter)
        if tag_filter:
            context["announcements"] = context["announcements"].filter(tags__name__icontains=tag_filter)

        paginator = Paginator(context["announcements"], 5)
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
