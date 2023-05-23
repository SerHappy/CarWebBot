from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
