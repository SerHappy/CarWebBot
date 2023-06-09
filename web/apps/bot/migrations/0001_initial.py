# Generated by Django 4.2.1 on 2023-06-15 11:42

from django.db import migrations
from django.db import models

import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("announcement", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublishedMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message_id", models.CharField(max_length=255)),
                ("channel_id", models.CharField(max_length=255)),
                ("type", models.CharField(choices=[("TEXT", "Text"), ("MEDIA", "Media")], max_length=20)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "announcement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="published_messages",
                        to="announcement.announcement",
                    ),
                ),
                (
                    "media",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="published_messages",
                        to="announcement.media",
                    ),
                ),
            ],
        ),
    ]
