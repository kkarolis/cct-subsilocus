import collections
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from reservations import exceptions
from reservations.models import MeetingRoom, Reservation
from reservations.validators import apply_overlap_filter

from . import utils

Interval = collections.namedtuple("Interval", ["start", "end"])


def generate_intervals(interval_definitions):
    """Generate an datetime intervals given timedelta tuples for easier testing.

    Interval definition is a tuple of (timedelta_end, timdelta_end) where where each
    timedelta is added to timezone.now() call
    """
    now = timezone.now()
    intervals = []
    for timedelta_start, timedelta_end in interval_definitions:
        start, end = utils.get_datetime_range(
            start=now, delta_start=timedelta_start, delta_end=timedelta_end
        )
        intervals.append(Interval(start=start, end=end))
    return intervals


class TestCaseCommonReservation(TestCase):
    fixtures = ["demo_data.json"]

    def setUp(self):
        super().setUp()
        self.meeting_room = MeetingRoom.objects.get(pk=1)
        self.meeting_room_1 = self.meeting_room
        self.meeting_room_2 = MeetingRoom.objects.get(pk=2)
        self.user = User.objects.get(pk=1)


class TestReservationCancelling(TestCaseCommonReservation):
    def test_successfull_reservation_cancel(self):
        # FIXME no title, why doesn't this fail?
        reservation = Reservation.objects.create(
            meeting_room=self.meeting_room,
            datetime_from=timezone.now() + timedelta(hours=1),
            datetime_to=timezone.now() + timedelta(hours=2),
            owner=self.user,
        )
        self.assertFalse(reservation.cancelled)
        reservation.cancel()
        self.assertTrue(reservation.cancelled)

    def test_cancelling_past_reservation_fails(self):
        reservation = Reservation.objects.create(
            meeting_room=self.meeting_room,
            datetime_from=timezone.now() - timedelta(hours=5),
            datetime_to=timezone.now() - timedelta(hours=3),
            owner=self.user,
        )
        self.assertFalse(reservation.cancelled)
        with self.assertRaises(exceptions.ReservationException):
            reservation.cancel()


class TestReservationTimeOvelapQSFilter(TestCaseCommonReservation):
    def create_reservation(self, **kwargs):
        """Return reservation payload with some sensible defaults (1 hour duration)."""
        dt_from, dt_to = utils.get_datetime_range(delta_end=timedelta(hours=1))
        values = {
            "title": "Reservation 1",
            "datetime_from": dt_from,
            "datetime_to": dt_to,
            "meeting_room": self.meeting_room,
            "owner": self.user,
        }
        values.update(**kwargs)
        reservation = Reservation(**values)
        reservation.save()
        return reservation

    def get_create_new_reservation_queryset(self, interval):
        """Create reservation and return queryset limited to this reservation."""
        reservation = self.create_reservation(
            datetime_from=interval[0], datetime_to=interval[1]
        )
        return Reservation.objects.all().filter(id=reservation.id)

    def generate_interval_test_scenario(self, first_offsets_hour, second_offsets_hour):
        """Create reservation for first interval and return start/end for second."""
        intervals = generate_intervals(
            [
                (timedelta(hours=start), timedelta(hours=end))
                for start, end in (first_offsets_hour, second_offsets_hour)
            ]
        )
        first, second = intervals[0], intervals[1]
        queryset = self.get_create_new_reservation_queryset(first)
        return queryset, second.start, second.end

    # tests below are named based on Allens interval notation
    # https://en.wikipedia.org/wiki/Allen%27s_interval_algebra
    def test_ovelap_first_before_second_does_not_overlap(self):
        queryset, start, end = self.generate_interval_test_scenario([-3, -2], [2, 3])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertFalse(overlap_queryset.exists())

    def test_overlap_second_after_first_does_not_overlap(self):
        queryset, start, end = self.generate_interval_test_scenario([2, 3], [-3, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertFalse(overlap_queryset.exists())

    def test_overlap_first_meets_second_does_not_overlap(self):
        queryset, start, end = self.generate_interval_test_scenario([-1, 0], [0, 1])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertFalse(overlap_queryset.exists())

    def test_overlap_second_meets_first_does_not_overlap(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 1], [-1, 0])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertFalse(overlap_queryset.exists())

    def test_overlap_case_overlap_exists(self):
        queryset, start, end = self.generate_interval_test_scenario([-1, 1], [0, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_inverse_overlap_exists(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 2], [-1, 1])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_first_starts_second_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 1], [0, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_second_starts_first_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 2], [0, 1])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_first_during_second_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 1], [-1, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_second_during_first_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([-1, 2], [0, 1])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_first_finishes_second_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([1, 2], [0, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_case_second_finishes_first_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 2], [1, 2])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())

    def test_overlap_first_equals_second_overlaps(self):
        queryset, start, end = self.generate_interval_test_scenario([0, 1], [0, 1])
        overlap_queryset = apply_overlap_filter(queryset, start, end)
        self.assertTrue(overlap_queryset.exists())
