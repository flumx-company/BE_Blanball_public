# Generated by Django 4.1.1 on 2022-10-24 11:03

import authentication.models
import django.core.validators
import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Code",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("verify_code", models.CharField(max_length=5, unique=True)),
                ("life_time", models.DateTimeField(blank=True, null=True)),
                ("type", models.CharField(max_length=20)),
                ("user_email", models.CharField(max_length=255)),
                ("dop_info", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "verbose_name": "code",
                "verbose_name_plural": "codes",
                "db_table": "code",
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                (
                    "gender",
                    models.CharField(
                        choices=[("Man", "Man"), ("Wooman", "Wooman")], max_length=10
                    ),
                ),
                (
                    "birthday",
                    models.DateField(
                        blank=True,
                        null=True,
                        validators=[authentication.models.validate_birthday],
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=authentication.models.image_file_name,
                    ),
                ),
                ("age", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "height",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(30),
                            django.core.validators.MaxValueValidator(210),
                        ],
                    ),
                ),
                (
                    "weight",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(30),
                            django.core.validators.MaxValueValidator(210),
                        ],
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("GK", "Gk"),
                            ("LB", "Lb"),
                            ("RB", "Rb"),
                            ("CB", "Cb"),
                            ("LWB", "Lwb"),
                            ("RWB", "Rwb"),
                            ("CDM", "Cdm"),
                            ("CM", "Cm"),
                            ("CAM", "Cam"),
                            ("RM", "Rm"),
                            ("LM", "Lm"),
                            ("RW", "Rw"),
                            ("LW", "Lw"),
                            ("RF", "Rf"),
                            ("CF", "Cf"),
                            ("LF", "Lf"),
                            ("ST", "St"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("about_me", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "profile",
                "verbose_name_plural": "profiles",
                "db_table": "profile",
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(db_index=True, max_length=255, unique=True),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, unique=True
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("is_online", models.BooleanField(default=False)),
                ("get_planned_events", models.CharField(default="1m", max_length=10)),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        choices=[("User", "User"), ("Admin", "Admin")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("raiting", models.FloatField(blank=True, null=True)),
                (
                    "configuration",
                    models.JSONField(default=authentication.models.configuration_dict),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user",
                        to="authentication.profile",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "db_table": "user",
            },
        ),
    ]