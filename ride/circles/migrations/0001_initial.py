# Generated by Django 3.1.13 on 2021-11-03 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Circle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Datetime on which the object was created",
                        verbose_name="created at",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Datetime on which the object was modified",
                        verbose_name="modified at",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="circle name")),
                ("slug_name", models.SlugField(unique=True)),
                (
                    "about",
                    models.CharField(max_length=255, verbose_name="circle description"),
                ),
                (
                    "picture",
                    models.ImageField(
                        blank=True, null=True, upload_to="circles/pictures"
                    ),
                ),
                ("rides_taken", models.PositiveIntegerField(default=0)),
                ("rides_offered", models.PositiveIntegerField(default=0)),
                (
                    "verified",
                    models.BooleanField(
                        default=False,
                        help_text="Verified circles are also known as official communities",
                        verbose_name="verified circle",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Public circles are listed in the main page so everyone know about their existence",
                        verbose_name="public field",
                    ),
                ),
                (
                    "is_limited",
                    models.BooleanField(
                        default=False,
                        help_text="Limited circles can grow up to a fixed number of members",
                        verbose_name="limited size circle",
                    ),
                ),
                (
                    "members_limit",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="If circle is limited, this will be the limit of the number of members",
                        verbose_name="limit of members in the circle",
                    ),
                ),
            ],
            options={
                "ordering": ["-rides_taken", "-rides_offered"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
    ]
