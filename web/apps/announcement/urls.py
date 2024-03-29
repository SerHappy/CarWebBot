from .views import AnnouncementCreateView
from .views import AnnouncementListView
from .views import AnnouncementUpdateView
from .views import delete_announcement
from .views import get_announcement_status
from .views import MediaUploadView
from .views import republish_announcement
from .views import takeoff_announcement
from django.urls import path


urlpatterns = [
    path("all/", AnnouncementListView.as_view(), name="announcement-list"),
    path("add/", AnnouncementCreateView.as_view(), name="announcement-add"),
    path("status/<int:pk>/", get_announcement_status, name="announcement-status"),
    path("edit/<int:pk>/", AnnouncementUpdateView.as_view(), name="announcement-edit"),
    path("takeoff/<int:pk>", takeoff_announcement, name="announcement-takeoff"),
    path("republish/<int:pk>/", republish_announcement, name="announcement-republish"),
    path("delete/<int:pk>/", delete_announcement, name="announcement-delete"),
    path("media/add/", MediaUploadView.as_view(), name="media-add"),
    path("media/delete/<path:upload_id>/", MediaUploadView.as_view(), name="media-delete"),
]
