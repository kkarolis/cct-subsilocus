from django.urls import reverse

from rest_framework import status

from .common import APITestCommonCase


class TestEmployeeEndpoint(APITestCommonCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("employee-list")

    def test_creating_employee(self):
        with self.get_authenticated_client() as client:
            response = client.post(self.url, {"name": "Ąrnold Švarcnėger"})
        self.assertStatusCode(status.HTTP_201_CREATED, response)

    def test_listing_employees(self):
        with self.get_authenticated_client() as client:
            self.assertStatusCode(status.HTTP_200_OK, client.get(self.url))

    def test_get_employee_details(self):
        url = reverse("employee-detail", kwargs={"pk": 1})
        with self.get_authenticated_client() as client:
            self.assertStatusCode(status.HTTP_200_OK, client.get(url))
