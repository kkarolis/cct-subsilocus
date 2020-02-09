"""subsilocus URL Configuration."""
from django.urls import include, path

from reservations import views
from rest_framework import routers
from rest_framework.authtoken import views as tokenviews

# FIXME add some documentation to generic api view
router = routers.DefaultRouter()
router.register(r"employees", views.EmployeeViewSet)
router.register(r"meeting-rooms", views.MeetingRoomViewSet)
router.register(r"reservations", views.ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api-token-auth/", tokenviews.obtain_auth_token),
]
