import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

GEOAPIFY_URL = os.getenv(
    "GEOAPIFY_URL",
    "https://api.geoapify.com/v2/places",
)

GEOAPIFY_API_KEY = os.getenv(
    "GEOAPIFY_API_KEY",
)


# ============================================================
# INVALID / NON-TOURIST PLACE KEYWORDS
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
    "bank",
    "atm",
    "insurance",
    "real estate",
    "property",
    "garage",
    "mechanic",
    "repair",
    "showroom",
    "workshop",
    "factory",
    "industrial",
    "warehouse",
    "business",
    "equipment",
    "technical",
    "residence",
    "apartment",
    "personal care",
    "salon",
    "dentist",
    "doctor",
    "laboratory",
    "transport company",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _normalize_name(value: Any) -> str:
    """
    Normalize place name for comparison/deduplication.
    """
    if value is None:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _is_valid_place_name(
    name: Any,
) -> bool:
    """
    Check whether the attraction name is valid.
    """

    if not name:
        return False

    normalized = _normalize_name(name)

    if not normalized:
        return False

    if normalized in {
        "unnamed place",
        "unknown",
        "unknown place",
        "place",
        "attraction",
    }:
        return False

    for keyword in INVALID_ATTRACTION_KEYWORDS:
        if keyword in normalized:
            return False

    return True


def _get_quality_score(
    properties: dict[str, Any],
) -> float:
    """
    Calculate a simple quality score.

    Higher score = more useful attraction.
    """

    score = 0.0

    categories = properties.get(
        "categories",
        [],
    )

    if isinstance(categories, list):
        category_text = " ".join(
            str(category).lower()
            for category in categories
        )
    else:
        category_text = str(
            categories or ""
        ).lower()

    # Strong tourist categories
    if "tourism.attraction" in category_text:
        score += 5

    if "tourism.sights" in category_text:
        score += 5

    if "tourism.museum" in category_text:
        score += 4

    if "tourism.heritage" in category_text:
        score += 4

    if "entertainment.culture" in category_text:
        score += 3

    if "leisure.park" in category_text:
        score += 3

    # Name available
    if properties.get("name"):
        score += 2

    # Address available
    if properties.get("formatted"):
        score += 1

    # Website available
    if properties.get("website"):
        score += 1

    # Opening hours available
    if properties.get("opening_hours"):
        score += 1

    # Phone available
    if properties.get("contact", {}).get("phone"):
        score += 0.5

    return score


def _extract_coordinates(
    feature: dict[str, Any],
    properties: dict[str, Any],
) -> tuple[float | None, float | None]:
    """
    Extract latitude and longitude safely.

    Geoapify normally returns:
        geometry.coordinates = [longitude, latitude]
    """

    geometry = feature.get(
        "geometry"
    ) or {}

    coordinates = geometry.get(
        "coordinates"
    ) or []

    longitude = None
    latitude = None

    if (
        isinstance(coordinates, list)
        and len(coordinates) >= 2
    ):
        longitude = _safe_float(
            coordinates[0],
            default=0.0,
        )

        latitude = _safe_float(
            coordinates[1],
            default=0.0,
        )

    # Fallback to properties
    if not longitude:
        longitude = properties.get(
            "lon"
        )

    if not latitude:
        latitude = properties.get(
            "lat"
        )

    longitude = (
        _safe_float(longitude)
        if longitude is not None
        else None
    )

    latitude = (
        _safe_float(latitude)
        if latitude is not None
        else None
    )

    # Invalid coordinates
    if (
        longitude is not None
        and latitude is not None
    ):
        if (
            longitude == 0
            and latitude == 0
        ):
            return None, None

    return latitude, longitude


# ============================================================
# MAIN GEOAPIFY ATTRACTION SEARCH
# ============================================================

async def search_attractions(
    latitude: float,
    longitude: float,
    radius: int = 5000,
) -> list[dict[str, Any]]:
    """
    Search tourist attractions around a location
    using Geoapify Places API.
    """

    api_key = (
        GEOAPIFY_API_KEY
        or os.getenv("GEOAPIFY_API_KEY")
    )

    if not api_key:
        print(
            "ERROR: GEOAPIFY_API_KEY "
            "is not configured."
        )
        return []

    # Validate coordinates
    latitude = _safe_float(latitude)
    longitude = _safe_float(longitude)

    if (
        latitude == 0
        and longitude == 0
    ):
        print(
            "ERROR: Invalid attraction coordinates."
        )
        return []

    # Keep radius within reasonable limits
    radius = max(
        1000,
        min(int(radius), 50000),
    )

    params = {
        "categories": (
            "tourism.attraction,"
            "tourism.sights,"
            "tourism.museum,"
            "tourism.heritage,"
            "leisure.park,"
            "entertainment.culture"
        ),
        "filter": (
            f"circle:"
            f"{longitude},"
            f"{latitude},"
            f"{radius}"
        ),
        "limit": 50,
        "apiKey": api_key,
    }

    try:
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                GEOAPIFY_URL,
                params=params,
            )

            response.raise_for_status()

            data = response.json()

        features = (
            data.get("features")
            or []
        )

        if not features:
            print(
                "Geoapify returned "
                "no attraction features."
            )
            return []

        results: list[
            dict[str, Any]
        ] = []

        seen_names: set[str] = set()

        for feature in features:

            if not isinstance(
                feature,
                dict,
            ):
                continue

            properties = (
                feature.get("properties")
                or {}
            )

            if not isinstance(
                properties,
                dict,
            ):
                continue

            # ------------------------------------------------
            # NAME
            # ------------------------------------------------

            name = (
                properties.get("name")
                or properties.get("address_line1")
                or ""
            )

            if not _is_valid_place_name(
                name
            ):
                continue

            normalized_name = (
                _normalize_name(name)
            )

            if normalized_name in seen_names:
                continue

            seen_names.add(
                normalized_name
            )

            # ------------------------------------------------
            # COORDINATES
            # ------------------------------------------------

            (
                attraction_latitude,
                attraction_longitude,
            ) = _extract_coordinates(
                feature,
                properties,
            )

            if (
                attraction_latitude
                is None
                or attraction_longitude
                is None
            ):
                continue

            # ------------------------------------------------
            # CATEGORIES
            # ------------------------------------------------

            categories = (
                properties.get(
                    "categories"
                )
                or []
            )

            if not isinstance(
                categories,
                list,
            ):
                categories = [
                    str(categories)
                ]

            # ------------------------------------------------
            # CONTACT INFORMATION
            # ------------------------------------------------

            contact = (
                properties.get(
                    "contact"
                )
                or {}
            )

            if not isinstance(
                contact,
                dict,
            ):
                contact = {}

            phone = (
                contact.get("phone")
                or properties.get("phone")
            )

            # ------------------------------------------------
            # QUALITY SCORE
            # ------------------------------------------------

            quality_score = (
                _get_quality_score(
                    properties
                )
            )

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            results.append(
                {
                    "name": str(name).strip(),

                    "address": (
                        properties.get(
                            "formatted"
                        )
                        or properties.get(
                            "address_line1"
                        )
                        or properties.get(
                            "address_line2"
                        )
                    ),

                    "latitude":
                        attraction_latitude,

                    "longitude":
                        attraction_longitude,

                    "categories":
                        categories,

                    "distance":
                        properties.get(
                            "distance"
                        ),

                    "website":
                        properties.get(
                            "website"
                        ),

                    "phone":
                        phone,

                    "opening_hours":
                        properties.get(
                            "opening_hours"
                        ),

                    "quality_score":
                        quality_score,

                    # Geoapify Places does not
                    # reliably provide ticket prices.
                    "ticket_price":
                        None,

                    "currency":
                        "INR",

                    "source":
                        "geoapify",
                }
            )

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        results.sort(
            key=lambda item: (
                -_safe_float(
                    item.get(
                        "quality_score"
                    )
                ),
                _safe_float(
                    item.get(
                        "distance"
                    ),
                    default=999999999,
                ),
            )
        )

        # Return maximum 30 attractions
        results = results[:30]

        print(
            f"Geoapify attractions found: "
            f"{len(results)}"
        )

        return results

    except httpx.HTTPStatusError as exc:

        print(
            "Attraction HTTP error:",
            exc.response.status_code,
        )

        try:
            print(
                "Geoapify response:",
                exc.response.text[:500],
            )
        except Exception:
            pass

        return []

    except httpx.RequestError as exc:

        print(
            "Attraction connection error:",
            repr(exc),
        )

        return []

    except Exception as exc:

        print(
            "Attraction error:",
            repr(exc),
        )

        return []


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

async def search_places(
    latitude: float,
    longitude: float,
    radius: int = 5000,
) -> list[dict[str, Any]]:
    """
    Backward-compatible alias.

    Some existing code may call search_places()
    instead of search_attractions().
    """

    return await search_attractions(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
    )


# ============================================================
# FALLBACK SEARCH
# ============================================================

async def search_attractions_with_fallback(
    latitude: float,
    longitude: float,
    radius: int = 10000,
) -> list[dict[str, Any]]:
    """
    Search attractions using multiple radius levels.

    Example:
        10 km
        20 km
        30 km
        50 km

    Stops early when enough attractions are found.
    """

    radius_levels = [
        max(1000, int(radius)),
        20000,
        30000,
        50000,
    ]

    # Remove duplicate radius values
    unique_radii = []

    for current_radius in radius_levels:
        if current_radius not in unique_radii:
            unique_radii.append(
                current_radius
            )

    all_results: list[
        dict[str, Any]
    ] = []

    seen_names: set[str] = set()

    for current_radius in unique_radii:

        print(
            f"Searching attractions "
            f"within {current_radius} meters..."
        )

        results = await search_attractions(
            latitude=latitude,
            longitude=longitude,
            radius=current_radius,
        )

        for item in results:

            name = _normalize_name(
                item.get("name")
            )

            if not name:
                continue

            if name in seen_names:
                continue

            seen_names.add(name)

            all_results.append(item)

        # If we have enough attractions,
        # stop expanding the search.
        if len(all_results) >= 5:
            break

    # Final sorting
    all_results.sort(
        key=lambda item: (
            -_safe_float(
                item.get(
                    "quality_score"
                )
            ),
            _safe_float(
                item.get(
                    "distance"
                ),
                default=999999999,
            ),
        )
    )

    all_results = all_results[:30]

    print(
        "Final unique attractions:",
        len(all_results),
    )

    return all_results