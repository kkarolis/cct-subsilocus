from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=100)

    # FIXME is this necessary?
    class Meta:
        ordering = ["id"]


class MeetingRoom(models.Model):
    name = models.CharField(max_length=100)

    # FIXME is this necessary?
    class Meta:
        ordering = ["id"]
