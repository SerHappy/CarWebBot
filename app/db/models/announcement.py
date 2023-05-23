from tortoise import fields
from tortoise.models import Model


class Announcement(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False)
    text = fields.TextField(null=False)
    price = fields.CharField(max_length=100, null=False)
    status = fields.CharField(max_length=50, null=False)
    tags: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.Tag",
        related_name="announcements",
        null=True,
    )
    note = fields.TextField(null=True)
    publication_date = fields.DatetimeField(auto_now_add=False, null=False)
    is_published = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
