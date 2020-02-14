import django_filters
from django_filters import rest_framework as filters
from reservations.models import Employee, MeetingRoom, Reservation


class EmployeeFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:  # noqa: D106
        model = Employee
        fields = ["id"]


class MeetingRoomFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:  # noqa: D106
        model = MeetingRoom
        fields = ["id"]


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class ReservationFilter(filters.FilterSet):
    employee_ids__in = NumberInFilter(field_name="employees", lookup_expr="in")

    # gte / lte might be useful as well
    datetime_from__lt = django_filters.IsoDateTimeFilter(
        field_name="datetime_from", lookup_expr="lt"
    )
    datetime_from__gt = django_filters.IsoDateTimeFilter(
        field_name="datetime_from", lookup_expr="gt"
    )
    datetime_to__lt = django_filters.IsoDateTimeFilter(
        field_name="datetime_to", lookup_expr="lt",
    )
    datetime_to__gt = django_filters.IsoDateTimeFilter(
        field_name="datetime_to", lookup_expr="gt",
    )

    class Meta:  # noqa: D106
        model = Reservation
        fields = {
            "id": ["exact"],
            "meeting_room_id": ["exact"],
            "title": ["icontains"],
            "cancelled": ["exact"],
        }
