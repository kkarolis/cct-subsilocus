from datetime import timedelta

from django.utils import timezone


# FIXME check, maybe theres something like this in Django ?
def format_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_datetime_range(start=None, delta_start=None, delta_end=None):
    """Generate start/end dates given optional timedelta instances added to start."""
    if start is None:
        start = timezone.now()

    start = start.replace(microsecond=0)
    interval_start = start + (delta_start if delta_start is not None else timedelta())
    interval_end = start + (delta_end if delta_end is not None else timedelta())
    return (interval_start, interval_end)
