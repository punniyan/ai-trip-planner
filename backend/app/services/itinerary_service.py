# app/services/itinerary_service.py

from datetime import date
from typing import Any


# ============================================================
# LOCAL CURRENCY
# ============================================================

DESTINATION_CURRENCY = {
    "dubai": "AED",
    "abu dhabi": "AED",
    "sharjah": "AED",

    "singapore": "SGD",

    "bangkok": "THB",

    "paris": "EUR",

    "london": "GBP",

    "tokyo": "JPY",

    "kuala lumpur": "MYR",

    "bali": "IDR",

    "new york": "USD",

    "los angeles": "USD",

    "maldives": "MVR",
}


# ============================================================
# INVALID ATTRACTION KEYWORDS
# ============================================================

INVALID_ATTRACTION_KEYWORDS = {
    "office",
    "clinic",
    "hospital",
    "medical",
    "pharmacy",
    "shop",
    "store",
    "supermarket",
    "grocery",
    "transport company",
    "equipment",
    "technical",
    "business center",
    "warehouse",
    "workshop",
    "factory",
    "industrial",
    "residence",
    "apartment",
    "personal care",
    "salon",
    "dentist",
    "doctor",
    "laboratory",
    "bank",
    "atm",
    "insurance",
    "real estate",
    "property",
    "garage",
    "mechanic",
    "repair shop",
    "showroom",
}


# ============================================================
# HELPERS
# ============================================================

def _parse_date(
    value: str,
) -> date:

    return date.fromisoformat(
        value
    )


def _normalize_name(
    value: Any,
) -> str:

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return default

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def _safe_quality_score(
    item: dict[str, Any],
) -> float:

    return _safe_float(
        item.get(
            "quality_score"
        ),
        0.0,
    )


def _local_currency(
    destination: str,
) -> str:

    normalized = (
        destination
        .strip()
        .lower()
    )

    return DESTINATION_CURRENCY.get(
        normalized,
        "INR",
    )


# ============================================================
# ATTRACTION VALIDATION
# ============================================================

def _is_valid_attraction(
    item: dict[str, Any],
) -> bool:

    if not isinstance(
        item,
        dict,
    ):
        return False

    name = str(
        item.get(
            "name",
            "",
        )
        or ""
    ).strip()

    if not name:
        return False

    normalized = _normalize_name(
        name
    )

    if normalized in {
        "unknown",
        "n/a",
        "na",
        "place",
        "location",
    }:
        return False

    for keyword in INVALID_ATTRACTION_KEYWORDS:

        if keyword in normalized:
            return False

    latitude = item.get(
        "latitude"
    )

    longitude = item.get(
        "longitude"
    )

    if (
        latitude is not None
        and longitude is not None
    ):

        try:

            float(latitude)
            float(longitude)

        except (
            TypeError,
            ValueError,
        ):

            return False

    return True


# ============================================================
# CLEAN PLACES
# ============================================================

def _clean_places(
    places: list[
        dict[str, Any]
    ]
    | None,
) -> list[dict[str, Any]]:

    if not places:
        return []

    cleaned = []

    seen: set[str] = set()

    for item in places:

        if not _is_valid_attraction(
            item
        ):
            continue

        name = _normalize_name(
            item.get("name")
        )

        if not name:
            continue

        if name in seen:
            continue

        seen.add(name)

        cleaned.append(item)

    cleaned.sort(
        key=lambda item: (
            -_safe_quality_score(
                item
            ),
            _safe_float(
                item.get("distance"),
                999999,
            ),
        )
    )

    return cleaned


# ============================================================
# CLEAN RESTAURANTS
# ============================================================

def _clean_restaurants(
    restaurants: list[
        dict[str, Any]
    ]
    | None,
) -> list[dict[str, Any]]:

    if not restaurants:
        return []

    cleaned = []

    seen: set[str] = set()

    for item in restaurants:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = str(
            item.get(
                "name",
                "",
            )
            or ""
        ).strip()

        if not name:
            continue

        normalized = _normalize_name(
            name
        )

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        cleaned.append(item)

    return cleaned


# ============================================================
# WEATHER
# ============================================================

def _get_weather_for_date(
    weather: list[
        dict[str, Any]
    ],
    target_date: str,
) -> dict[str, Any] | None:

    for item in weather:

        if not isinstance(
            item,
            dict,
        ):
            continue

        if str(
            item.get(
                "date",
                "",
            )
        ) == target_date:

            return item

    return None


# ============================================================
# SELECT PLACES
# ============================================================

def _select_places_for_day(
    places: list[
        dict[str, Any]
    ],
    used_places: set[str],
    max_places: int = 2,
) -> list[dict[str, Any]]:

    selected = []

    for place in places:

        name = _normalize_name(
            place.get("name")
        )

        if not name:
            continue

        if name in used_places:
            continue

        selected.append(place)

        used_places.add(
            name
        )

        if len(selected) >= max_places:
            break

    return selected


# ============================================================
# SELECT RESTAURANT
# ============================================================

def _select_restaurant_for_day(
    restaurants: list[
        dict[str, Any]
    ],
    used_restaurants: set[str],
    day_index: int,
) -> dict[str, Any] | None:

    if not restaurants:
        return None

    for restaurant in restaurants:

        name = _normalize_name(
            restaurant.get("name")
        )

        if not name:
            continue

        if name not in used_restaurants:

            used_restaurants.add(
                name
            )

            return restaurant

    return restaurants[
        day_index % len(restaurants)
    ]


# ============================================================
# CREATE ITINERARY
# ============================================================

def create_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    places: list[
        dict[str, Any]
    ]
    | None,
    restaurants: list[
        dict[str, Any]
    ]
    | None,
    weather: list[
        dict[str, Any]
    ]
    | None,
) -> list[dict[str, Any]]:

    cleaned_places = _clean_places(
        places or []
    )

    cleaned_restaurants = _clean_restaurants(
        restaurants or []
    )

    weather_data = weather or []

    start = _parse_date(
        start_date
    )

    end = _parse_date(
        end_date
    )

    if end < start:

        raise ValueError(
            "End date cannot be before start date."
        )

    local_currency = _local_currency(
        destination
    )

    itinerary = []

    used_places: set[str] = set()

    used_restaurants: set[str] = set()

    current = start

    day_index = 0

    while current <= end:

        date_string = current.isoformat()

        selected_places = (
            _select_places_for_day(
                cleaned_places,
                used_places,
                max_places=2,
            )
        )

        selected_restaurant = (
            _select_restaurant_for_day(
                cleaned_restaurants,
                used_restaurants,
                day_index,
            )
        )

        weather_for_day = (
            _get_weather_for_date(
                weather_data,
                date_string,
            )
        )

        activities = []

        # ====================================================
        # MORNING
        # ====================================================

        if len(selected_places) >= 1:

            place = selected_places[0]

            activities.append(
                {
                    "time": "09:00",
                    "type": "attraction",
                    "name": place.get("name"),
                    "address": place.get("address"),
                    "latitude": place.get("latitude"),
                    "longitude": place.get("longitude"),
                    "duration_hours": 2,
                    "ticket_price": place.get(
                        "ticket_price"
                    ),
                    "currency": (
                        local_currency
                        if place.get(
                            "ticket_price"
                        )
                        is not None
                        else None
                    ),
                    "source": place.get(
                        "source",
                        "geoapify",
                    ),
                }
            )

        # ====================================================
        # AFTERNOON
        # ====================================================

        if len(selected_places) >= 2:

            place = selected_places[1]

            activities.append(
                {
                    "time": "14:00",
                    "type": "attraction",
                    "name": place.get("name"),
                    "address": place.get("address"),
                    "latitude": place.get("latitude"),
                    "longitude": place.get("longitude"),
                    "duration_hours": 2,
                    "ticket_price": place.get(
                        "ticket_price"
                    ),
                    "currency": (
                        local_currency
                        if place.get(
                            "ticket_price"
                        )
                        is not None
                        else None
                    ),
                    "source": place.get(
                        "source",
                        "geoapify",
                    ),
                }
            )

        # ====================================================
        # EVENING RESTAURANT
        # ====================================================

        if selected_restaurant:

            activities.append(
                {
                    "time": "19:00",
                    "type": "restaurant",
                    "name": selected_restaurant.get(
                        "name"
                    ),
                    "address": selected_restaurant.get(
                        "address"
                    ),
                    "latitude": selected_restaurant.get(
                        "latitude"
                    ),
                    "longitude": selected_restaurant.get(
                        "longitude"
                    ),
                    "price": selected_restaurant.get(
                        "price"
                    ),
                    "price_range": selected_restaurant.get(
                        "price_range"
                    ),

                    # IMPORTANT:
                    # Never trust hard-coded INR
                    # from Geoapify normalization.
                    "currency": local_currency,

                    "source": selected_restaurant.get(
                        "source",
                        "geoapify",
                    ),
                }
            )

        itinerary.append(
            {
                "day": day_index + 1,
                "date": date_string,
                "destination": destination,
                "weather": weather_for_day,
                "activities": activities,
            }
        )

        current = current.fromordinal(
            current.toordinal() + 1
        )

        day_index += 1

    return itinerary