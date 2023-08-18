from django.db import models


class Tag(models.Model):
    """Класс модели тегов."""

    class TagType(models.TextChoices):
        """Класс типов тегов."""

        visible = "visible", "Visible"
        hidden = "hidden", "Hidden"

    name: str = models.CharField(max_length=50, unique=True)
    is_active: bool = models.BooleanField(default=True)
    # TODO: Fix A003 error by renaming built-in `type` field to something else
    type: str = models.CharField(  # noqa: A003
        max_length=20,
        choices=TagType.choices,
        null=False,
        default=TagType.visible,
    )
    channel_id: int = models.CharField(max_length=255, blank=True)
    modified_at: str = models.DateTimeField(auto_now=True)
    created_at: str = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета-класс для модели тегов."""

        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        """Строковое представление тега."""
        return f"Tag {self.name} of type {self.type}"
