# Generated by Django 4.2.1 on 2023-05-29 12:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("announcement", "0003_alter_tag_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="announcement",
            name="price",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="announcement",
            name="publication_date",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="announcement",
            name="status",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="announcement",
            name="text",
            field=models.TextField(null=True),
        ),
    ]
