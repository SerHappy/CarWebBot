from django.db import models


class Setting(models.Model):
    unpublish_date = models.DateTimeField(null=True, blank=True)
