from django.db import models


class Tag(models.Model):
    class TagType(models.TextChoices):
        visible = "visible", "Visible"
        hidden = "hidden", "Hidden"

    name: str = models.CharField(max_length=50, unique=True)
    is_active: bool = models.BooleanField(default=True)
    type: str = models.CharField(
        max_length=20,
        choices=TagType.choices,
        null=False,
        default=TagType.visible,
    )
    channel_id: str = models.CharField(max_length=255, null=True, blank=True)
    modified_at: str = models.DateTimeField(auto_now=True)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Tag {self.name} of type {self.type}"
