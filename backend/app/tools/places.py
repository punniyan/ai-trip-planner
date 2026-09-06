from typing import Any

import re
import sys

import httpx

from app.config import settings


# ============================================================
# WINDOWS / UTF-8 TERMINAL SUPPORT
# ============================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace",
    )

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace",
    )


# ============================================================
# GEOAPIFY
# ============================================================

GEOAPIFY_PLACES_URL = (
    "https://api.geoapify.com/v2/places"
)

GEOAPIFY_GEOCODING_URL = (
    "https://api.geoapify.com/v1/geocode/search"
)


# ============================================================
# GEOAPIFY SUPPORTED ATTRACTION CATEGORIES
# ============================================================

ATTRACTION_CATEGORIES = [
    "tourism",
    "heritage",
    "leisure",
    "entertainment",
]


# ============================================================
# INVALID PLACE KEYWORDS
# ============================================================

INVALID_ATTRACTION_KEYWORDS = {
    # Business / commercial
    "office",
    "business center",
    "business centre",
    "company",
    "corporate",
    "head office",
    "corporate office",
    "building",
    "tower",

    # Medical
    "clinic",
    "hospital",
    "medical",
    "pharmacy",
    "dentist",
    "doctor",

    # Shopping / grocery
    "shop",
    "store",
    "supermarket",
    "super market",
    "grocery",
    "market",
    "minimart",
    "mini mart",

    # Financial
    "bank",
    "atm",
    "exchange",

    # Education
    "school",
    "college",
    "university",
    "institute",
    "academy",

    # Transport / logistics
    "transport company",
    "transportation company",
    "shipping",
    "shipping company",
    "cargo",
    "freight",
    "logistics",
    "warehouse",
    "courier",

    # Vehicle
    "car rental",
    "car rental company",
    "car parked",
    "parking",
    "parking lot",
    "parking area",
    "garage",

    # Residential
    "residential building",
    "apartment",
    "apartment building",
    "residence",

    # Generic infrastructure
    "street",
    "road",
    "highway",
    "bridge",
    "tunnel",
    "roundabout",
    "junction",
    "intersection",

    # Utility / infrastructure
    "post office",
    "police station",
    "fire station",
    "government office",
    "government building",

    # Personal / service businesses
    "personal care",
    "salon",
    "beauty salon",
    "barber",
    "laundry",
    "repair",
    "service center",
    "service centre",
}


# ============================================================
# INVALID CATEGORY KEYWORDS
# ============================================================

INVALID_CATEGORY_KEYWORDS = {
    "commercial",
    "commercial.building",
    "building",
    "building.office",
    "building.commercial",
    "building.residential",
    "parking",
    "parking.park_and_ride",
    "service",
    "industrial",
    "industrial.facility",
    "transport",
    "transport.bus",
    "transport.taxi",
    "logistics",
}


# ============================================================
# GENERIC / LOW QUALITY NAMES
# ============================================================

GENERIC_INVALID_NAMES = {
    "",
    "unnamed",
    "unnamed attraction",
    "unknown",
    "unknown place",
    "place",
    "attraction",
    "point of interest",
    "poi",
}


# ============================================================
# HELPERS
# ============================================================

def _safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    """
    Safely convert a value to float.
    """
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _clean_text(value: Any) -> str:
    """
    Convert any value to a clean string.
    """
    if value is None:
        return ""

    text = str(value)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _normalize_name(name: str) -> str:
    """
    Normalize place name for comparison.
    """

    text = _clean_text(name).lower()

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9\u0600-\u06ff\u0900-\u097f\s]",
        " ",
        text,
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _is_invalid_place(
    name: str,
    categories: list[str],
) -> bool:
    """
    Detect obvious non-tourist places.
    """

    normalized_name = _normalize_name(name)

    normalized_categories = [
        _normalize_name(category)
        for category in categories
    ]

    category_text = " ".join(
        normalized_categories
    )

    # --------------------------------------------------------
    # Empty / generic names
    # --------------------------------------------------------

    if normalized_name in {
        _normalize_name(name)
        for name in GENERIC_INVALID_NAMES
    }:
        return True

    # --------------------------------------------------------
    # Check name
    # --------------------------------------------------------

    for keyword in INVALID_ATTRACTION_KEYWORDS:

        keyword_normalized = _normalize_name(
            keyword
        )

        if not keyword_normalized:
            continue

        if keyword_normalized in normalized_name:
            return True

    # --------------------------------------------------------
    # Check categories
    # --------------------------------------------------------

    for keyword in INVALID_CATEGORY_KEYWORDS:

        keyword_normalized = _normalize_name(
            keyword
        )

        if keyword_normalized in category_text:
            return True

    return False


def _is_valid_coordinates(
    latitude: float | None,
    longitude: float | None,
) -> bool:
    """
    Validate latitude and longitude.
    """

    if latitude is None or longitude is None:
        return False

    if not -90 <= latitude <= 90:
        return False

    if not -180 <= longitude <= 180:
        return False

    return True


def _is_duplicate_by_distance(
    place: dict[str, Any],
    existing_places: list[dict[str, Any]],
    coordinate_tolerance: float = 0.0005,
) -> bool:
    """
    Detect nearby duplicate POIs.

    0.0005 degrees is roughly around 50 meters.
    """

    name = _normalize_name(
        place.get("name", "")
    )

    latitude = _safe_float(
        place.get("latitude")
    )

    longitude = _safe_float(
        place.get("longitude")
    )

    if latitude is None or longitude is None:
        return False

    for existing in existing_places:

        existing_name = _normalize_name(
            existing.get("name", "")
        )

        existing_latitude = _safe_float(
            existing.get("latitude")
        )

        existing_longitude = _safe_float(
            existing.get("longitude")
        )

        if (
            existing_latitude is None
            or existing_longitude is None
        ):
            continue

        # ----------------------------------------------------
        # Exact normalized name
        # ----------------------------------------------------

        if name and name == existing_name:

            latitude_difference = abs(
                latitude - existing_latitude
            )

            longitude_difference = abs(
                longitude - existing_longitude
            )

            if (
                latitude_difference
                <= coordinate_tolerance
                and
                longitude_difference
                <= coordinate_tolerance
            ):
                return True

    return False


# ============================================================
# GET GEOAPIFY API KEY
# ============================================================

def _get_geoapify_api_key() -> str | None:
    """
    Get Geoapify API key from application settings.
    """

    api_key = getattr(
        settings,
        "geoapify_api_key",
        None,
    )

    if not api_key:
        print(
            "[places] ERROR: "
            "GEOAPIFY_API_KEY is missing"
        )

        return None

    return str(api_key).strip()


# ============================================================
# GEOCODE CITY / DESTINATION
# ============================================================

async def _geocode_location(
    location: str,
) -> tuple[float | None, float | None]:
    """
    Convert city/destination name into latitude/longitude
    using Geoapify Geocoding API.
    """

    location = _clean_text(location)

    if not location:
        print(
            "[places] Geocoding skipped: "
            "empty city/destination"
        )

        return None, None

    api_key = _get_geoapify_api_key()

    if not api_key:
        return None, None

    print(
        "\n[places] ========================================"
    )

    print(
        "[places] LOCATION GEOCODING"
    )

    print(
        f"[places] Search location: {location}"
    )

    print(
        "[places] ========================================"
    )

    params = {
        "text": location,
        "limit": 1,
        "apiKey": api_key,
    }

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                GEOAPIFY_GEOCODING_URL,
                params=params,
            )

            print(
                "[places] Geocoding HTTP status: "
                f"{response.status_code}"
            )

            if response.status_code != 200:

                print(
                    "[places] Geocoding error response:"
                )

                print(
                    response.text[:3000]
                )

                return None, None

            try:

                data = response.json()

            except ValueError as exc:

                print(
                    "[places] Geocoding JSON error:",
                    repr(exc),
                )

                return None, None

            results = (
                data.get(
                    "results",
                    [],
                )
                or []
            )

            print(
                "[places] Geocoding results: "
                f"{len(results)}"
            )

            if not results:

                print(
                    "[places] No coordinates found "
                    f"for: {location}"
                )

                return None, None

            result = results[0]

            latitude = _safe_float(
                result.get("lat")
            )

            longitude = _safe_float(
                result.get("lon")
            )

            formatted = _clean_text(
                result.get("formatted")
            )

            print(
                f"[places] Geocoded location: "
                f"{formatted}"
            )

            print(
                f"[places] Latitude: {latitude}"
            )

            print(
                f"[places] Longitude: {longitude}"
            )

            if not _is_valid_coordinates(
                latitude,
                longitude,
            ):

                print(
                    "[places] ERROR: "
                    "Invalid geocoded coordinates"
                )

                return None, None

            return latitude, longitude

    except httpx.TimeoutException as exc:

        print(
            "[places] Geocoding timeout:",
            repr(exc),
        )

        return None, None

    except httpx.RequestError as exc:

        print(
            "[places] Geocoding request error:",
            repr(exc),
        )

        return None, None

    except Exception as exc:

        print(
            "[places] Geocoding unexpected error:",
            repr(exc),
        )

        return None, None


# ============================================================
# NORMALIZE PLACE
# ============================================================

def _normalize_place(
    feature: dict[str, Any],
) -> dict[str, Any]:

    properties = (
        feature.get(
            "properties",
            {},
        )
        or {}
    )

    geometry = (
        feature.get(
            "geometry",
            {},
        )
        or {}
    )

    coordinates = (
        geometry.get(
            "coordinates",
            [],
        )
        or []
    )

    # ========================================================
    # COORDINATES
    # ========================================================

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

    latitude = _safe_float(
        latitude
    )

    longitude = _safe_float(
        longitude
    )

    # ========================================================
    # NAME
    # ========================================================

    name = (
        properties.get("name")
        or properties.get("address_line1")
        or properties.get("address_line2")
        or "Unnamed Attraction"
    )

    name = _clean_text(name)

    # ========================================================
    # CATEGORIES
    # ========================================================

    categories = (
        properties.get(
            "categories",
            [],
        )
        or []
    )

    if isinstance(
        categories,
        str,
    ):
        categories = [
            categories
        ]

    categories = [
        _clean_text(category)
        for category in categories
        if _clean_text(category)
    ]

    # ========================================================
    # ADDRESS
    # ========================================================

    address = (
        properties.get("formatted")
        or properties.get("address_line2")
        or properties.get("address_line1")
        or ""
    )

    address = _clean_text(
        address
    )

    # ========================================================
    # WEBSITE
    # ========================================================

    website = (
        properties.get("website")
        or properties.get("url")
    )

    if website:
        website = _clean_text(
            website
        )

    # ========================================================
    # PHONE
    # ========================================================

    phone = (
        properties.get("phone")
        or properties.get("contact:phone")
    )

    if phone:
        phone = _clean_text(
            phone
        )

    # ========================================================
    # OPENING HOURS
    # ========================================================

    opening_hours = (
        properties.get(
            "opening_hours"
        )
    )

    if opening_hours:
        opening_hours = _clean_text(
            opening_hours
        )

    # ========================================================
    # DISTANCE
    # ========================================================

    distance = _safe_float(
        properties.get(
            "distance"
        )
    )

    # ========================================================
    # PLACE ID
    # ========================================================

    place_id = (
        properties.get("place_id")
        or properties.get("datasource")
        or feature.get("id")
    )

    if place_id:
        place_id = _clean_text(
            place_id
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "name": name,
        "category": "attraction",
        "categories": categories,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance,
        "website": website,
        "phone": phone,
        "opening_hours": opening_hours,
        "place_id": place_id,
        "source": "geoapify",
    }


# ============================================================
# SEARCH PLACES
# ============================================================

async def search_places(
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = 5000,
    city: str | None = None,
    destination: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search tourist attractions.

    Supported arguments:

        search_places(
            latitude=25.2647,
            longitude=55.2924,
            radius=10000,
        )

    OR:

        search_places(
            city="Dubai",
        )

    OR:

        search_places(
            destination="Dubai",
        )

    OR:

        search_places(
            city="Dubai",
            destination="Dubai",
        )

    If latitude/longitude are not provided,
    city/destination will be geocoded automatically.
    """

    print(
        "\n[places] ========================================"
    )

    print(
        "[places] ATTRACTION SEARCH"
    )

    print(
        "[places] ========================================"
    )

    print(
        f"[places] City: {city}"
    )

    print(
        f"[places] Destination: {destination}"
    )

    print(
        f"[places] Latitude: {latitude}"
    )

    print(
        f"[places] Longitude: {longitude}"
    )

    print(
        f"[places] Radius: {radius}"
    )

    print(
        "[places] ========================================"
    )

    # ========================================================
    # API KEY
    # ========================================================

    api_key = _get_geoapify_api_key()

    if not api_key:
        return []

    # ========================================================
    # LOCATION FALLBACK
    #
    # Priority:
    # 1. latitude + longitude
    # 2. city
    # 3. destination
    # ========================================================

    latitude = _safe_float(
        latitude
    )

    longitude = _safe_float(
        longitude
    )

    if not _is_valid_coordinates(
        latitude,
        longitude,
    ):

        location_name = (
            _clean_text(city)
            or _clean_text(destination)
        )

        if not location_name:

            print(
                "[places] ERROR: "
                "No latitude/longitude, "
                "city, or destination provided"
            )

            return []

        print(
            "[places] Coordinates not available."
        )

        print(
            "[places] Trying Geoapify geocoding "
            f"for: {location_name}"
        )

        latitude, longitude = await _geocode_location(
            location_name
        )

    # ========================================================
    # FINAL COORDINATE VALIDATION
    # ========================================================

    if not _is_valid_coordinates(
        latitude,
        longitude,
    ):

        print(
            "[places] ERROR: "
            "Unable to determine valid coordinates"
        )

        return []

    # ========================================================
    # VALIDATE RADIUS
    # ========================================================

    try:

        radius = int(radius)

    except (TypeError, ValueError):

        radius = 5000

    if radius <= 0:
        radius = 5000

    # Prevent unnecessarily large requests
    radius = min(
        radius,
        50000,
    )

    print(
        "[places] FINAL SEARCH COORDINATES:"
    )

    print(
        f"[places] Latitude: {latitude}"
    )

    print(
        f"[places] Longitude: {longitude}"
    )

    print(
        f"[places] Radius: {radius}"
    )

    # ========================================================
    # GEOAPIFY REQUEST
    # ========================================================

    params = {
        "categories": ",".join(
            ATTRACTION_CATEGORIES
        ),
        "filter": (
            f"circle:{longitude},"
            f"{latitude},"
            f"{radius}"
        ),
        "limit": 50,
        "apiKey": api_key,
    }

    print(
        "[places] Geoapify request:"
    )

    print(
        f"[places] URL: "
        f"{GEOAPIFY_PLACES_URL}"
    )

    print(
        f"[places] Categories: "
        f"{params['categories']}"
    )

    print(
        f"[places] Filter: "
        f"{params['filter']}"
    )

    # ========================================================
    # API CALL
    # ========================================================

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                GEOAPIFY_PLACES_URL,
                params=params,
            )

            print(
                "[places] HTTP status: "
                f"{response.status_code}"
            )

            # =================================================
            # API ERROR
            # =================================================

            if response.status_code != 200:

                print(
                    "[places] ERROR RESPONSE:"
                )

                print(
                    response.text[:3000]
                )

                return []

            # =================================================
            # JSON
            # =================================================

            try:

                data = response.json()

            except ValueError as exc:

                print(
                    "[places] JSON ERROR:",
                    repr(exc),
                )

                return []

            features = (
                data.get(
                    "features",
                    [],
                )
                or []
            )

            print(
                "[places] Raw features: "
                f"{len(features)}"
            )

            # =================================================
            # NORMALIZE + FILTER
            # =================================================

            results: list[
                dict[str, Any]
            ] = []

            filtered_count = 0
            invalid_coordinate_count = 0
            duplicate_count = 0

            for index, feature in enumerate(
                features
            ):

                try:

                    # -----------------------------------------
                    # Feature validation
                    # -----------------------------------------

                    if not isinstance(
                        feature,
                        dict,
                    ):
                        continue

                    # -----------------------------------------
                    # Normalize
                    # -----------------------------------------

                    place = _normalize_place(
                        feature
                    )

                    name = place.get(
                        "name",
                        "Unnamed Attraction",
                    )

                    categories = place.get(
                        "categories",
                        [],
                    )

                    print(
                        f"\n[places] Place "
                        f"{index + 1}: {name}"
                    )

                    print(
                        f"[places] Categories: "
                        f"{categories}"
                    )

                    print(
                        f"[places] Coordinates: "
                        f"{place.get('latitude')}, "
                        f"{place.get('longitude')}"
                    )

                    # -----------------------------------------
                    # Coordinate validation
                    # -----------------------------------------

                    if not _is_valid_coordinates(
                        place.get("latitude"),
                        place.get("longitude"),
                    ):

                        print(
                            "[places] Skipping "
                            f"{name}: "
                            "invalid coordinates"
                        )

                        invalid_coordinate_count += 1

                        continue

                    # -----------------------------------------
                    # Invalid place filter
                    # -----------------------------------------

                    if _is_invalid_place(
                        str(name),
                        categories,
                    ):

                        print(
                            "[places] Filtered invalid: "
                            f"{name}"
                        )

                        filtered_count += 1

                        continue

                    # -----------------------------------------
                    # Duplicate filter
                    # -----------------------------------------

                    if _is_duplicate_by_distance(
                        place,
                        results,
                    ):

                        print(
                            "[places] Filtered duplicate: "
                            f"{name}"
                        )

                        duplicate_count += 1

                        continue

                    # -----------------------------------------
                    # Add result
                    # -----------------------------------------

                    results.append(
                        place
                    )

                except Exception as exc:

                    print(
                        "[places] Normalize error:",
                        repr(exc),
                    )

            # =================================================
            # FINAL RESULTS
            # =================================================

            print(
                "\n[places] ========================================"
            )

            print(
                "[places] Raw features: "
                f"{len(features)}"
            )

            print(
                "[places] Invalid filtered: "
                f"{filtered_count}"
            )

            print(
                "[places] Invalid coordinates: "
                f"{invalid_coordinate_count}"
            )

            print(
                "[places] Duplicates filtered: "
                f"{duplicate_count}"
            )

            print(
                "[places] Final attractions: "
                f"{len(results)}"
            )

            # =================================================
            # PRINT FINAL ATTRACTIONS
            # =================================================

            if results:

                print(
                    "\n[places] FINAL ATTRACTIONS:"
                )

                for index, place in enumerate(
                    results,
                    start=1,
                ):

                    print(
                        "\n[places] "
                        f"========== Attraction {index} =========="
                    )

                    print(
                        "[places] Name: "
                        f"{place.get('name')}"
                    )

                    print(
                        "[places] Address: "
                        f"{place.get('address')}"
                    )

                    print(
                        "[places] Categories: "
                        f"{place.get('categories')}"
                    )

                    print(
                        "[places] Latitude: "
                        f"{place.get('latitude')}"
                    )

                    print(
                        "[places] Longitude: "
                        f"{place.get('longitude')}"
                    )

                    print(
                        "[places] Website: "
                        f"{place.get('website')}"
                    )

                    print(
                        "[places] Opening Hours: "
                        f"{place.get('opening_hours')}"
                    )

            else:

                print(
                    "[places] WARNING: "
                    "No valid attractions found"
                )

            print(
                "\n[places] ========================================"
            )

            return results

    # ========================================================
    # TIMEOUT
    # ========================================================

    except httpx.TimeoutException as exc:

        print(
            "[places] TIMEOUT ERROR:",
            repr(exc),
        )

        return []

    # ========================================================
    # REQUEST ERROR
    # ========================================================

    except httpx.RequestError as exc:

        print(
            "[places] REQUEST ERROR:",
            repr(exc),
        )

        return []

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as exc:

        print(
            "[places] UNEXPECTED ERROR:",
            repr(exc),
        )

        return []


# ============================================================
# FALLBACK SEARCH
# ============================================================

async def search_attractions_with_fallback(
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = 10000,
    city: str | None = None,
    destination: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fallback attraction search.

    Supports:
        latitude + longitude

    OR:
        city

    OR:
        destination
    """

    print(
        "\n[places] Running attraction fallback"
    )

    results = await search_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        city=city,
        destination=destination,
    )

    return results