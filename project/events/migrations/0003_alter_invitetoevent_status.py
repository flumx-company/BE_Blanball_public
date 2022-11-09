# Generated by Django 4.1.1 on 2022-10-26 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_invitetoevent_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invitetoevent",
            name="status",
            field=models.CharField(
                choices=[("Accepted", "Accepted"), ("Declined", "Declined")],
                default=None,
                max_length=10,
                null=True,
            ),
        ),
    ]