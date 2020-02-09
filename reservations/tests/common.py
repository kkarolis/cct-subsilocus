import contextlib

from django.contrib.auth.models import User

from rest_framework.test import APITestCase


class APITestCommonCase(APITestCase):
    fixtures = ["demo_data.json"]

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(pk=1)

    @contextlib.contextmanager
    def get_authenticated_client(self, user=None):
        client = self.client
        try:
            client.force_authenticate(user=user if user is not None else self.user)
            yield client
        finally:
            client.logout()

    def assertStatusCode(self, status_code, response):
        self.assertEqual(status_code, response.status_code, response.data)
