from reservations.models import Employee, MeetingRoom, Reservation
from reservations.validators import NonOverlappingReservationValidator
from rest_framework import serializers


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:  # noqa: D106
        model = Employee
        fields = ["id", "name", "url", "owner"]


class MeetingRoomSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:  # noqa: D106
        model = MeetingRoom
        fields = ["id", "name", "url", "owner"]


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    employee_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="employees",
        write_only=True,
        many=True,
        default=[],
    )
    meeting_room = MeetingRoomSerializer(read_only=True)
    meeting_room_id = serializers.PrimaryKeyRelatedField(
        queryset=MeetingRoom.objects.all(), source="meeting_room", write_only=True
    )
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:  # noqa: D106
        model = Reservation
        fields = [
            "id",
            "url",
            "title",
            "datetime_from",
            "datetime_to",
            "meeting_room",
            "meeting_room_id",
            "cancelled",
            "employees",
            "employee_ids",
            "owner",
        ]
        validators = [
            NonOverlappingReservationValidator(
                queryset=Reservation.objects.all().filter(cancelled=False)
            )
        ]

    def validate(self, data):

        # only works for create, updates would require fetching columns
        # do not allow out of order dates
        # assume "microsecond" meetings is ok
        if data["datetime_from"] > data["datetime_to"]:
            raise serializers.ValidationError(
                "Reservation to date must be greater than from date"
            )

        # assume reservations in past are ok as well. The use case could be for logging
        # purposes, to log a "happened" reservation
        return super().validate(data)
