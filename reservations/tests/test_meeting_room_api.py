from django.urls import reverse

from rest_framework import status

from .common import APITestCommonCase


class TestMeetingRoomEndpoint(APITestCommonCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("meetingroom-list")

    def test_creating_meeting_room(self):
        with self.get_authenticated_client() as client:
            response = client.post(self.url, {"name": "Spėčial Room€"})
        self.assertStatusCode(status.HTTP_201_CREATED, response)

    def test_listing_meeting_rooms(self):
        with self.get_authenticated_client() as client:
            self.assertStatusCode(status.HTTP_200_OK, client.get(self.url))

    def test_get_meeting_room_details(self):
        url = reverse("meetingroom-detail", kwargs={"pk": 1})
        with self.get_authenticated_client() as client:
            self.assertStatusCode(status.HTTP_200_OK, client.get(url))
