# pylint: disable=missing-docstring, too-few-public-methods

from datetime import timedelta

class DurationRounder():
    def __init__(self, round_to_minutes):
        self.round_to = timedelta(minutes=round_to_minutes)
        self.rounding_boundary = self.round_to / 2.0

    def round(self, duration):
        quotient, remainder = divmod(duration, self.round_to)

        if duration == timedelta(0):
            return duration
        if quotient == 0 and remainder > timedelta(0):
            return self.round_to
        if remainder >= self.rounding_boundary:
            return (quotient + 1) * self.round_to
        return quotient * self.round_to
