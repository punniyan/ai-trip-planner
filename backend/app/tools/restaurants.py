# app/tools/restaurants.py

from typing import Any

import httpx

from app.config import settings


# ============================================================
# GEOAPIFY URL
# ============================================================

GEOAPIFY_URL = (
    settings.geoapify_url
    or "https://api.geoapify.com/v2/places"
)


# ============================================================
# HELPERS
# ============================================================

def _safe_float(
    value: Any,
) -> float | None:

    try:

        if value is None:
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


def _safe_text(
    value: Any,
) -> str | None:

    if value is None:
        return None

    text = str(
        value
    ).strip()

    return text or None


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


# ============================================================
# SEARCH RESTAURANTS
# ============================================================

async def search_restaurants(
    latitude: float,
    longitude: float,
    radius: int = 15000,
    limit: int = 30,
) -> list[dict[str, Any]]:

    if not settings.geoapify_api_key:
        print(
            "GEOAPIFY_API_KEY not configured."
        )
        return []

    radius = max(
        1000,
        min(
            int(radius),
            50000,
        ),
    )

    limit = max(
        1,
        min(
            int(limit),
            50,
        ),
    )

    params = {
        "categories": (
            "catering.restaurant,"
            "catering.cafe,"
            "catering.fast_food"
        ),
        "filter": (
            f"circle:"
            f"{longitude},"
            f"{latitude},"
            f"{radius}"
        ),
        "limit": limit,
        "apiKey": settings.geoapify_api_key,
    }

    try:

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            response = await client.get(
                GEOAPIFY_URL,
                params=params,
            )

            response.raise_for_status()

            data = response.json()

    except Exception as error:

        print(
            "Restaurant API error:",
            error,
        )

        return []

    results: list[
        dict[str, Any]
    ] = []

    seen: set[str] = set()

    for feature in data.get(
        "features",
        [],
    ):

        properties = feature.get(
            "properties",
            {},
        )

        geometry = feature.get(
            "geometry",
            {},
        )

        coordinates = geometry.get(
            "coordinates",
            [],
        )

        if (
            not isinstance(
                coordinates,
                list,
            )
            or len(coordinates) < 2
        ):
            continue

        longitude_value = _safe_float(
            coordinates[0]
        )

        latitude_value = _safe_float(
            coordinates[1]
        )

        if (
            longitude_value is None
            or latitude_value is None
        ):
            continue

        name = _safe_text(
            properties.get(
                "name"
            )
        )

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

        categories = properties.get(
            "categories",
            [],
        )

        if not isinstance(
            categories,
            list,
        ):
            categories = []

        contact = properties.get(
            "contact",
            {},
        )

        phone = None

        if isinstance(
            contact,
            dict,
        ):
            phone = (
                contact.get("phone")
            )

        results.append(
            {
                "name": name,
                "address": _safe_text(
                    properties.get(
                        "formatted"
                    )
                ),
                "latitude": latitude_value,
                "longitude": longitude_value,
                "categories": categories,
                "distance": _safe_float(
                    properties.get(
                        "distance"
                    )
                ),
                "website": _safe_text(
                    properties.get(
                        "website"
                    )
                ),
                "phone": phone,
                "opening_hours": _safe_text(
                    properties.get(
                        "opening_hours"
                    )
                ),
                "quality_score": 1,
                "price": None,
                "price_range": None,
                "currency": "INR",
                "source": "geoapify",
            }
        )

    results.sort(
        key=lambda item: (
            item.get(
                "distance"
            )
            or 999999
        )
    )

    return results[:limit]