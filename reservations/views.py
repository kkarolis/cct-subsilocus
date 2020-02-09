import logging

from reservations.exceptions import ReservationException
from reservations.filters import EmployeeFilter, MeetingRoomFilter, ReservationFilter
from reservations.models import Employee, MeetingRoom, Reservation
from reservations.permissions import IsOwner
from reservations.serializers import (
    EmployeeSerializer,
    MeetingRoomSerializer,
    ReservationSerializer,
)
from rest_framework import decorators, mixins, permissions, serializers, viewsets
from rest_framework.response import Response

_logger = logging.getLogger(__name__)


# for now we are not interested DELETEing/PATCHing from API
class CreateReadViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    def perform_create(self, serializer):
        res = super().perform_create(serializer)
        if (
            hasattr(self, "create_log_message")
            and self.create_log_message
            and serializer.instance is not None
        ):
            _logger.info()
        return res


class EmployeeViewSet(CreateReadViewSet):
    """API endpoint for managing employee records."""

    permission_classes = [permissions.IsAuthenticated]

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    filterset_class = EmployeeFilter

    def perform_create(self, serializer):
        res = super().perform_create(serializer)
        if serializer.instance is not None:
            _logger.info("Employee(id=%s)", serializer.instance.id)
        return res


class MeetingRoomViewSet(CreateReadViewSet):
    """API endpoint for managing meeting room records."""

    permission_classes = [permissions.IsAuthenticated]

    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer

    filterset_class = MeetingRoomFilter

    def perform_create(self, serializer):
        res = super().perform_create(serializer)
        if serializer.instance is not None:
            _logger.info("MeetingRoom(id=%s) created", serializer.instance.id)
        return res


class ReservationViewSet(CreateReadViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    filterset_fields = ["cancelled", "meeting_room_id", "title"]
    filterset_class = ReservationFilter

    def perform_create(self, serializer):
        res = super().perform_create(serializer)
        if serializer.instance is not None:
            instance = serializer.instance
            _logger.info(
                "Reservation(id=%(reservation_id)s) created for "
                "MeetingRoom(id=%(meeting_room_id)s)",
                {
                    "reservation_id": instance.id,
                    "meeting_room_id": instance.meeting_room.id,
                },
            )
        return res

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsOwner])
    def cancel(self, request, pk=None):
        # will raise 404 if not found
        instance = self.get_object()
        try:
            instance.cancel()
            instance.save()
        # FIXME operational errors? would need to log them
        except ReservationException as exc:
            raise serializers.ValidationError(
                detail=serializers.as_serializer_error(exc)
            )
        else:
            _logger.info("Reservation(id=%s) cancelled", instance.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
