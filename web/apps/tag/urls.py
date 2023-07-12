from .views import check_tag
from .views import TagCreation
from .views import TagListView
from django.urls import path
from .views import TagEditView

urlpatterns = [
    path("all/", TagListView.as_view(), name="tag-list"),
    path("add/", TagCreation.as_view(), name="tag-add"),
    path("edit/<int:pk>/", TagEditView.as_view(), name="tag-edit"),
    # path("delete/<int:pk>/", ..., name="tag-delete"),
    path("check-tag/", check_tag, name="check-tag"),
]
