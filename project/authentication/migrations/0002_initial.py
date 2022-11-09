from django.contrib.postgres import operations
from django.db import migrations


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        operations.TrigramExtension(),
    ]
