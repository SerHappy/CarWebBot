from .views import check_tag
from .views import delete_tag
from .views import TagCreateView
from .views import TagEditView
from .views import TagListView
from django.urls import path


urlpatterns = [
    path("all/", TagListView.as_view(), name="tag-list"),
    path("add/", TagCreateView.as_view(), name="tag-add"),
    path("edit/<int:pk>/", TagEditView.as_view(), name="tag-edit"),
    path("delete/<int:pk>/", delete_tag, name="tag-delete"),
    path("check-tag/", check_tag, name="check-tag"),
]
