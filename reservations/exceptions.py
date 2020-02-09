from django.core.exceptions import ValidationError


class ReservationException(ValidationError):
    """General exception raised by apps business logic."""
