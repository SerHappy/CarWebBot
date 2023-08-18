from django.db import models


class Setting(models.Model):
    """Класс модели настроек."""

    unpublish_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Мета-класс для модели настроек."""

        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

    def __str__(self):
        """Строковое представление настроек."""
        return f"Настройки. Дата снятии с публикации: {self.unpublish_date}"
