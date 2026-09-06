from typing import Any

import httpx

from app.config import settings


GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"


HOTEL_CATEGORIES = [
    "accommodation.hotel",
    "accommodation.motel",
    "accommodation.guest_house",
    "accommodation.hostel",
]


def _safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_property(properties: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = properties.get(key)
        if value not in (None, ""):
            return value
    return None


def _normalize_hotel(
    feature: dict[str, Any],
    destination: str,
    check_in: str | None,
    check_out: str | None,
    travelers: int,
) -> dict[str, Any]:

    properties = feature.get("properties", {}) or {}

    geometry = feature.get("geometry", {}) or {}
    coordinates = geometry.get("coordinates", []) or []

    longitude = (
        coordinates[0]
        if len(coordinates) > 0
        else properties.get("lon")
    )

    latitude = (
        coordinates[1]
        if len(coordinates) > 1
        else properties.get("lat")
    )

    name = (
        properties.get("name")
        or properties.get("address_line1")
        or "Hotel"
    )

    address = (
        properties.get("formatted")
        or properties.get("address_line2")
        or properties.get("address_line1")
        or destination
    )

    price = _safe_float(
        _get_property(
            properties,
            "price",
            "price_per_night",
            "amount",
        )
    )

    website = _get_property(
        properties,
        "website",
        "url",
    )

    phone = _get_property(
        properties,
        "contact:phone",
        "phone",
    )

    opening_hours = _get_property(
        properties,
        "opening_hours",
    )

    place_id = _get_property(
        properties,
        "place_id",
        "datasource",
    )

    distance = _safe_float(
        properties.get("distance")
    )

    return {
        "name": name,
        "destination": destination,
        "address": address,
        "latitude": _safe_float(latitude),
        "longitude": _safe_float(longitude),
        "distance": distance,
        "categories": properties.get("categories", []),
        "price": price,
        "price_per_night": price,
        "currency": "AED",
        "price_status": (
            "available"
            if price is not None
            else "not_available"
        ),
        "website": website,
        "opening_hours": opening_hours,
        "phone": phone,
        "place_id": place_id,
        "check_in": check_in,
        "check_out": check_out,
        "travelers": travelers,
        "source": "geoapify",
    }


async def search_hotels(
    destination: str,
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = 10000,
    check_in: str | None = None,
    check_out: str | None = None,
    travelers: int = 1,
) -> list[dict[str, Any]]:

    print("\n[hotels] ========================================")
    print("[hotels] HOTEL SEARCH")
    print(f"[hotels] Destination: {destination}")
    print(f"[hotels] Latitude: {latitude}")
    print(f"[hotels] Longitude: {longitude}")
    print(f"[hotels] Radius: {radius}")
    print(f"[hotels] Check-in: {check_in}")
    print(f"[hotels] Check-out: {check_out}")
    print(f"[hotels] Travelers: {travelers}")

    if latitude is None or longitude is None:
        print("[hotels] ERROR: latitude/longitude required")
        return []

    api_key = getattr(settings, "geoapify_api_key", None)

    if not api_key:
        print("[hotels] ERROR: GEOAPIFY_API_KEY is missing")
        return []

    params = {
        "categories": ",".join(HOTEL_CATEGORIES),
        "filter": f"circle:{longitude},{latitude},{radius}",
        "limit": 20,
        "apiKey": api_key,
    }

    print(f"[hotels] URL: {GEOAPIFY_PLACES_URL}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                GEOAPIFY_PLACES_URL,
                params=params,
            )

            print(
                f"[hotels] HTTP status: {response.status_code}"
            )

            if response.status_code != 200:
                print(
                    "[hotels] ERROR:",
                    response.text[:1000],
                )
                return []

            data = response.json()

            features = data.get("features", []) or []

            print(
                f"[hotels] Geoapify features: {len(features)}"
            )

            results: list[dict[str, Any]] = []

            for feature in features:

                try:
                    hotel = _normalize_hotel(
                        feature=feature,
                        destination=destination,
                        check_in=check_in,
                        check_out=check_out,
                        travelers=travelers,
                    )

                    if hotel["name"]:
                        results.append(hotel)

                except Exception as exc:
                    print(
                        "[hotels] Normalize error:",
                        repr(exc),
                    )

            print(
                f"[hotels] Final results: {len(results)}"
            )

            return results

    except Exception as exc:

        print(
            "[hotels] Request error:",
            repr(exc),
        )

        return []