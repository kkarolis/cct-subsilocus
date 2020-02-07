from reservations.models import Employee, MeetingRoom
from rest_framework import serializers


# technically not necessary, but it'll help debugging
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["name"]


class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = ["name"]
