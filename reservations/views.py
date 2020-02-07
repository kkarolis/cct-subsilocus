from rest_framework import viewsets
from reservations.models import Employee, MeetingRoom
from reservations.serializers import EmployeeSerializer, MeetingRoomSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """API endpoint listing all users."""

    # FIXME add order
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class MeetingRoomViewSet(viewsets.ModelViewSet):
    """API Endpoint listing all the meeting rooms."""

    # FIXME add order
    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer
