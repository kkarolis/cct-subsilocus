# Generated by Django 3.0.3 on 2020-02-08 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0004_auto_20200207_1025"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="employees",
            field=models.ManyToManyField(to="reservations.Employee"),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="meeting_room",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="reservations.MeetingRoom",
            ),
        ),
    ]
