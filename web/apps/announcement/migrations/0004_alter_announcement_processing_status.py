# Generated by Django 4.2.1 on 2023-08-12 17:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("announcement", "0003_remove_announcement_is_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="announcement",
            name="processing_status",
            field=models.CharField(
                choices=[
                    ("AWAITING", "Awaiting Publication"),
                    ("PUBLISHED", "Published"),
                    ("UNPUBLISHED", "Unpublished"),
                    ("INACTIVE", "Inactive"),
                    ("PROCESSING", "Processing"),
                    ("ERROR", "Error"),
                ],
                default="AWAITING",
                max_length=20,
            ),
        ),
    ]
