from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q, constraints
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from reservations.exceptions import ReservationException


class Employee(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:  # noqa: D106
        ordering = ["id"]

    def __str__(self):
        return self.name


class MeetingRoom(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:  # noqa: D106
        ordering = ["id"]

    def __str__(self):
        return self.name


class Reservation(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    # don't track other status, cancelled as bool should be good enough for now
    cancelled = models.BooleanField(default=False)

    # FIXME its assumed datetime fields are be stored in UTC time, maybe in Django its
    # handled nicely ?
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()

    meeting_room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE)

    employees = models.ManyToManyField(Employee)

    class Meta:  # noqa: D106
        ordering = ["id"]
        constraints = [
            constraints.CheckConstraint(
                check=Q(datetime_to__gt=F("datetime_from")), name="datetime_to_gt_from"
            )
        ]

    def __str__(self):
        return self.title

    # FIXME check if fat models is ok in django?
    def cancel(self):
        if self.cancelled:
            return

        # for data consistency do not allow cancelling past meetings
        now = timezone.now()
        if self.datetime_from is not None and self.datetime_from < now:
            raise ReservationException(_("Only future reservations can be cancelled"))

        self.cancelled = True
