from tortoise import fields
from tortoise.models import Model


class Media(Model):
    id = fields.IntField(pk=True)
    media_type = fields.CharField(max_length=20)
    url = fields.CharField(max_length=255)
    publication: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.Announcement",
        related_name="media",
        null=False,
        on_delete=fields.CASCADE,
    )
