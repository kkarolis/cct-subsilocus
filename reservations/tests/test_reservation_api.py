from datetime import timedelta

from django.urls import reverse

from reservations.models import Employee, MeetingRoom
from rest_framework import status

from . import utils
from .common import APITestCommonCase


def get_datetime_range_serialized(**kwargs):
    """Return same datetime range as get_datetime_range, but in ISO 8601 format."""
    start, end = utils.get_datetime_range(**kwargs)
    return utils.format_datetime(start), utils.format_datetime(end)


class TestReservationEndpoint(APITestCommonCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("reservation-list")
        self.meeting_room = MeetingRoom.objects.get(pk=1)
        self.meeting_room_1 = self.meeting_room
        self.meeting_room_2 = MeetingRoom.objects.get(pk=2)
        self.employee_1 = Employee.objects.get(pk=1)
        self.employee_2 = Employee.objects.get(pk=2)

    def _get_reservation_payload(self, **kwargs):
        """Return reservation payload with some sensible defaults (1 hour duration)."""
        dt_from, dt_to = get_datetime_range_serialized(delta_end=timedelta(hours=1))
        values = {
            "title": "Reservation 1",
            "datetime_from": dt_from,
            "datetime_to": dt_to,
            "meeting_room_id": self.meeting_room.id,
        }
        values.update(**kwargs)
        return values

    def generate_reservation(self, client, **kwargs):
        payload = self._get_reservation_payload(**kwargs)
        return client.post(self.url, payload)

    def test_listing_reservations(self):
        with self.get_authenticated_client() as client:
            response = client.get(self.url)
            self.assertStatusCode(status.HTTP_200_OK, response)
            self.assertTrue(response.data["count"] >= 1)

    def test_get_reservation_details(self):
        url = reverse("reservation-detail", kwargs={"pk": 1})
        with self.get_authenticated_client() as client:
            self.assertStatusCode(status.HTTP_200_OK, client.get(url))

    def test_creating_reservation(self):
        with self.get_authenticated_client() as client:
            response = self.generate_reservation(client)
            self.assertStatusCode(status.HTTP_201_CREATED, response)

    def test_create_reservation_with_employees(self):
        with self.get_authenticated_client() as client:
            response = self.generate_reservation(
                client, employee_ids=[self.employee_1.id, self.employee_2.id]
            )
            self.assertStatusCode(status.HTTP_201_CREATED, response)

    def test_creating_overlaping_meeting_for_same_room_workflow(self):
        dt_from, dt_to = get_datetime_range_serialized(
            delta_start=timedelta(hours=1), delta_end=timedelta(hours=3)
        )

        def create_same_room_reservation(client):
            return self.generate_reservation(
                client=client,
                datetime_from=dt_from,
                datetime_to=dt_to,
                meeting_room=self.meeting_room.id,
            )

        with self.get_authenticated_client() as client:
            response_1 = create_same_room_reservation(client)
            response_2 = create_same_room_reservation(client)

            self.assertStatusCode(status.HTTP_201_CREATED, response_1)
            self.assertStatusCode(status.HTTP_400_BAD_REQUEST, response_2)

            # cancel the first one and try again, should succeed now
            first_reservation_id = response_1.data["id"]
            url = reverse("reservation-detail", kwargs={"pk": first_reservation_id})

            cancel_response = client.post(url + "cancel/")
            self.assertStatusCode(status.HTTP_200_OK, cancel_response)

            response_3 = create_same_room_reservation(client)
            self.assertStatusCode(status.HTTP_201_CREATED, response_3)

    def test_creating_reservation_same_employee_in_2_meetings_fails(self):
        dt_from, dt_to = get_datetime_range_serialized(delta_end=timedelta(hours=1))
        with self.get_authenticated_client() as client:
            response_1 = self.generate_reservation(
                client,
                datetime_form=dt_from,
                datetime_to=dt_to,
                meeting_room_id=self.meeting_room_1.id,
                employee_ids=[self.employee_1.id, self.employee_2.id],
            )
            response_2 = self.generate_reservation(
                client,
                datetime_form=dt_from,
                datetime_to=dt_to,
                meeting_room_id=self.meeting_room_2.id,
                employee_ids=[self.employee_1.id],
            )
            self.assertStatusCode(status.HTTP_201_CREATED, response_1)
            self.assertStatusCode(status.HTTP_400_BAD_REQUEST, response_2)
