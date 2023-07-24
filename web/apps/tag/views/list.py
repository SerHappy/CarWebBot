from apps.tag.models import Tag
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.views.generic import ListView
from loguru import logger
from typing import Any


class TagListView(LoginRequiredMixin, ListView):
    login_url = settings.LOGIN_URL
    model = Tag
    template_name = "tag/tag_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        name_filter = self.request.GET.get("nameFilter", None)
        if name_filter:
            context["tags"] = context["tags"].filter(name__icontains=name_filter)

        paginator = Paginator(context["tags"], 10)
        page = self.request.GET.get("page")
        try:
            context["tags"] = paginator.page(page)
            logger.info(f"Page {page} of tags was loaded")
        except (PageNotAnInteger, ValueError):
            logger.warning(f"Page {page} of tags was not an integer")
            context["tags"] = paginator.page(1)
            logger.info(f"Page 1 of tags was loaded")
        except EmptyPage:
            logger.warning(f"Page {page} of tags was empty")
            context["tags"] = paginator.page(paginator.num_pages)
            logger.info(f"Last page of tags was loaded")
        except InvalidPage:
            logger.warning(f"Page {page} of tags was invalid")
            context["tags"] = paginator.page(1)
            logger.info(f"Page 1 of tags was loaded")
        return context
