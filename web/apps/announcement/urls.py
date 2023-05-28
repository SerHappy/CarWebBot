from .views import AnnouncementCreation
from .views import AnnouncementListView
from .views import AnnouncementUpdate
from .views import disable_announcement
from .views import enable_announcement
from .views import get_announcement_status
from .views import publish_announcement
from .views import republish_announcement
from .views import TagCreation
from django.urls import path


urlpatterns = [
    path("all/", AnnouncementListView.as_view(), name="announcement-list"),
    path("add/", AnnouncementCreation.as_view(), name="announcement-add"),
    path("status/<int:pk>/", get_announcement_status, name="announcement-status"),
    path("tags/add/", TagCreation.as_view(), name="tag-add"),
    path("edit/<int:pk>/", AnnouncementUpdate.as_view(), name="announcement-edit"),
    path("disable/<int:pk>/", disable_announcement, name="announcement-disable"),
    path("enable/<int:pk>/", enable_announcement, name="announcement-activate"),
    path("republish/<int:pk>/", republish_announcement, name="announcement-republish"),
    path("publish/<int:pk>/", publish_announcement, name="announcement-publish"),
]
