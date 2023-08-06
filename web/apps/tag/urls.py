from .views import TagCheckView
from .views import TagCreateView
from .views import TagDeleteView
from .views import TagListView
from .views import TagUpdateView
from django.urls import path


urlpatterns = [
    path("all/", TagListView.as_view(), name="tag-list"),
    path("add/", TagCreateView.as_view(), name="tag-add"),
    path("edit/<int:pk>/", TagUpdateView.as_view(), name="tag-edit"),
    path("delete/<int:pk>/", TagDeleteView.as_view(), name="tag-delete"),
    path("check-tag/", TagCheckView.as_view(), name="check-tag"),
]
