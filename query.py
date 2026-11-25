"""Running queries against the flight database."""

import math
from datetime import datetime


VALID_FIELDS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def valid_datetime(value: str) -> bool:
    """Check datetime format."""
    if not isinstance(value, str):
        return False

    try:
        parsed = datetime.strptime(value, DATETIME_FORMAT)
        return parsed.strftime(DATETIME_FORMAT) == value
    except ValueError:
        return False


def valid_number(value) -> bool:
    """Check that a value is a finite number."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object."""

    if not isinstance(query, dict):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": [],
        }

    allowed_keys = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
        "min_price",
        "sort_by",
        "order",
        "limit",
    }

    if any(key not in allowed_keys for key in query):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": [],
        }

    # Validate exact-match fields
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate departure datetime
    if "departure_datetime" in query:
        if not valid_datetime(query["departure_datetime"]):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate arrival datetime
    if "arrival_datetime" in query:
        if not valid_datetime(query["arrival_datetime"]):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate price
    if "price" in query:
        if not valid_number(query["price"]):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate minimum price
    if "min_price" in query:
        if not valid_number(query["min_price"]):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate sorting
    if "sort_by" in query:
        if query["sort_by"] not in VALID_FIELDS:
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    if "order" in query:
        if query["order"] not in ("asc", "desc"):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

        if "sort_by" not in query:
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    # Validate limit
    if "limit" in query:
        limit = query["limit"]

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 0
        ):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": [],
            }

    matches = []

    for flight in db:
        matched = True

        # Exact match filters
        for key in ("flight_id", "origin", "destination"):
            if key in query and flight.get(key) != query[key]:
                matched = False
                break

        if not matched:
            continue

        # Departure must be >= requested datetime
        if "departure_datetime" in query:
            if flight.get("departure_datetime", "") < query["departure_datetime"]:
                continue

        # Arrival must be <= requested datetime
        if "arrival_datetime" in query:
            if flight.get("arrival_datetime", "") > query["arrival_datetime"]:
                continue

        # Maximum price
        if "price" in query:
            if flight.get("price", float("inf")) > query["price"]:
                continue

        # Minimum price
        if "min_price" in query:
            if flight.get("price", float("-inf")) < query["min_price"]:
                continue

        matches.append(flight)

    # Sorting
    if "sort_by" in query:
        sort_field = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"

        matches.sort(
            key=lambda flight: flight.get(sort_field),
            reverse=reverse,
        )

    # Limit results
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches,
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of queries."""

    if isinstance(queries, dict):
        queries = [queries]

    if not isinstance(queries, list):
        return [
            {
                "query": queries,
                "error": "INVALID_QUERY",
                "matches": [],
            }
        ]

    return [run_query(db, query) for query in queries]

