from django.urls import path
from .views import check_tag
from .views import TagCreation
urlpatterns = [
    # path("all/", ..., name="tag-all"),
    path("add/", TagCreation.as_view(), name="tag-add"),
    # path("edit/<int:pk>/", ..., name="tag-edit"),
    # path("delete/<int:pk>/", ..., name="tag-delete"),
    path("check-tag/", check_tag, name="check-tag"),
]
