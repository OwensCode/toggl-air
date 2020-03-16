# pylint: disable=missing-docstring

from decimal import Decimal, ROUND_HALF_UP

def calc_rounded_hours(rounded_duration):
    hours = Decimal.from_float(rounded_duration.total_seconds()) / 60 / 60
    return hours.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
