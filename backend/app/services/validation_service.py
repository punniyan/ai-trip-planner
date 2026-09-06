# app/services/validation_service.py

from datetime import date
from typing import Any


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value: Any) -> date | None:
    """
    Convert YYYY-MM-DD string to date.
    """

    if value is None:
        return None

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


# ============================================================
# INTEGER PARSER
# ============================================================

def parse_int(value: Any) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# FLOAT PARSER
# ============================================================

def parse_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# TRIP VALIDATION
# ============================================================

def validate_trip(trip: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and normalize trip data.
    """

    result = dict(trip)

    # --------------------------------------------------------
    # Destination
    # --------------------------------------------------------

    destination = result.get("destination")

    if destination is not None:
        destination = str(destination).strip()

    result["destination"] = destination or None

    # --------------------------------------------------------
    # Origin
    # --------------------------------------------------------

    origin = result.get("origin")

    if origin is not None:
        origin = str(origin).strip()

    result["origin"] = origin or None

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    start_date = parse_date(result.get("start_date"))
    end_date = parse_date(result.get("end_date"))

    result["start_date"] = (
        start_date.isoformat()
        if start_date
        else None
    )

    result["end_date"] = (
        end_date.isoformat()
        if end_date
        else None
    )

    # --------------------------------------------------------
    # Travelers
    # --------------------------------------------------------

    travelers = parse_int(
        result.get("travelers")
    )

    if travelers is not None and travelers < 1:
        travelers = 1

    result["travelers"] = travelers

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    currency = result.get("currency")

    if currency is not None:
        currency = str(currency).strip().upper()

    result["currency"] = currency or "INR"

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    budget = parse_float(
        result.get("budget")
    )

    if budget is not None and budget < 0:
        budget = 0

    result["budget"] = budget or 0

    # --------------------------------------------------------
    # Date consistency
    # --------------------------------------------------------

    if start_date and end_date:
        if end_date < start_date:
            result["date_error"] = (
                "End date cannot be before start date."
            )

    return result


# ============================================================
# REQUIRED DATE CHECK
# ============================================================

def requires_dates(
    trip: dict[str, Any],
) -> bool:

    start_date = parse_date(
        trip.get("start_date")
    )

    end_date = parse_date(
        trip.get("end_date")
    )

    return (
        start_date is None
        or end_date is None
    )


# ============================================================
# REQUIRED FIELD CHECK
# ============================================================

def get_missing_fields(
    trip: dict[str, Any],
) -> list[str]:

    missing: list[str] = []

    if not trip.get("destination"):
        missing.append("destination")

    if not trip.get("origin"):
        missing.append("origin")

    if not trip.get("start_date"):
        missing.append("start_date")

    if not trip.get("end_date"):
        missing.append("end_date")

    if not trip.get("travelers"):
        missing.append("travelers")

    return missing


# ============================================================
# TRIP DAYS
# ============================================================

def calculate_trip_days(
    start_date: Any,
    end_date: Any,
) -> int:

    start = parse_date(start_date)
    end = parse_date(end_date)

    if not start or not end:
        return 0

    if end < start:
        return 0

    return (end - start).days + 1


# ============================================================
# TRIP NIGHTS
# ============================================================

def calculate_trip_nights(
    start_date: Any,
    end_date: Any,
) -> int:

    start = parse_date(start_date)
    end = parse_date(end_date)

    if not start or not end:
        return 0

    if end < start:
        return 0

    return (end - start).days


# ============================================================
# FINAL VALIDATION
# ============================================================

def is_valid_trip(
    trip: dict[str, Any],
) -> bool:

    validated = validate_trip(trip)

    missing = get_missing_fields(
        validated
    )

    if missing:
        return False

    if validated.get("date_error"):
        return False

    return True