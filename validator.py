"""Row validation: airport list loading, single-row checks, record building."""

import csv
import math
import re
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M"
FLIGHT_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{2,8}$")
AIRPORT_PATTERN = re.compile(r"^[A-Z]{3}$")
DATETIME_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$")


def load_airports(path: str) -> set[str]:
    """Read airport codes, ignoring blank lines and comments."""
    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if not code or code.startswith("#"):
                continue

            airports.add(code)

    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Return the first validation error, or None if the row is valid."""

    # 1. Wrong field count
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]

    flight_id, origin, destination, departure, arrival, price = fields

    # 2. Missing field
    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    # 3. Invalid flight ID
    if not FLIGHT_ID_PATTERN.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    # 4. Invalid origin
    if not AIRPORT_PATTERN.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    # 5. Invalid destination
    if not AIRPORT_PATTERN.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    # 6. Same origin and destination
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # 7. Invalid departure datetime
    if not DATETIME_PATTERN.fullmatch(departure):
        return "INVALID_DEPARTURE"

    try:
        departure_dt = datetime.strptime(departure, DATETIME_FORMAT)
    except ValueError:
        return "INVALID_DEPARTURE"

    # 8. Invalid arrival datetime
    if not DATETIME_PATTERN.fullmatch(arrival):
        return "INVALID_ARRIVAL"

    try:
        arrival_dt = datetime.strptime(arrival, DATETIME_FORMAT)
    except ValueError:
        return "INVALID_ARRIVAL"

    # 9. Arrival must be after departure
    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10. Invalid price
    try:
        price_value = float(price)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    # 11. Price must be positive
    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Convert a valid CSV row into a flight record."""

    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5]),
    }
