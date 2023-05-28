from .models import Announcement
from .models import Media
from .models import Tag
from django import forms


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["media_type", "file"]


class AnnouncementForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)
    media = forms.ModelChoiceField(queryset=Media.objects.all())

    class Meta:
        model = Announcement
        fields = [
            "name",
            "text",
            "price",
            "tags",
            "status",
            "media",
            "note",
            "publication_date",
        ]
