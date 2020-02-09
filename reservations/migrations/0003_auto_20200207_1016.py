# Generated by Django 3.0.3 on 2020-02-07 10:16

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0002_reservation"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.CheckConstraint(
                check=models.Q(
                    datetime_from__gt=django.db.models.expressions.F("datetime_to")
                ),
                name="datetime_to_gt_from",
            ),
        ),
    ]
