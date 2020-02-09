from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import qs_exists, qs_filter


def apply_overlap_filter(queryset, start, end):
    """Filter QS, picking out overlapping records for given start/end dates."""
    return qs_filter(queryset, datetime_from__lt=end, datetime_to__gt=start)


# credits: https://git.io/JvnmX
class NonOverlappingReservationValidator:
    requires_context = True

    def __init__(self, queryset):
        self.queryset = queryset
        self.required_fields = ["datetime_from", "datetime_to", "meeting_room"]

    def enforce_required_fields(self, attrs, serializer):
        """Require datetime ranges and room fields to be set."""
        if serializer.instance is not None:
            return

        missing_items = {
            field_name: _("This field is required.")
            for field_name in self.required_fields
            if serializer.fields[field_name].source not in attrs
        }
        if missing_items:
            raise serializers.ValidationError(missing_items, code="required")

    def __call__(self, attrs, serializer):
        self.enforce_required_fields(attrs, serializer)

        queryset = self.queryset
        start, end = attrs["datetime_from"], attrs["datetime_to"]
        queryset = apply_overlap_filter(queryset, start, end)

        meeting_room_overlap = qs_filter(queryset, meeting_room=attrs["meeting_room"])
        if qs_exists(meeting_room_overlap):
            # minimal information on error message, assume thats ok
            raise serializers.ValidationError(
                _("This room has an overlapping reservation"), code="overlap"
            )

        employees = attrs["employees"]
        if employees:
            employee_overlap = qs_filter(queryset, employees__in=employees)
            if qs_exists(employee_overlap):
                # in reality, indicating which employee and which reservation overlaps
                # would be helpful
                raise serializers.ValidationError(
                    _("Employee has a different overlapping reservation already"),
                    code="overlap",
                )
