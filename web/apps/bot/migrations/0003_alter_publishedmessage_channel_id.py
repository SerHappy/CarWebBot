# Generated by Django 4.2.1 on 2023-08-12 12:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0002_alter_publishedmessage_channel_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="publishedmessage",
            name="channel_id",
            field=models.CharField(max_length=255),
        ),
    ]
