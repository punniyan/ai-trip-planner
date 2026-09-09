import httpx
from typing import Any

from app.config import settings


STAYING_API_URL = "https://api.stayingapi.com/v1/search"


def _safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _get_hotel_image(
    hotel: dict[str, Any],
) -> str | None:
    """
    Get the first valid image URL from StayingAPI response.
    StayingAPI returns images as:
        "images": [
            "https://....jpg"
        ]
    """

    images = hotel.get("images")

    # images = ["url1", "url2", ...]
    if isinstance(images, list):
        for image in images:
            if isinstance(image, str) and image.strip():
                return image.strip()

    # images = "url"
    if isinstance(images, str) and images.strip():
        return images.strip()

    return None


def _normalize_hotel(
    hotel: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert StayingAPI hotel response
    into frontend-friendly hotel object.
    """

    location = hotel.get("location") or {}
    price = hotel.get("price") or {}
    identity = hotel.get("identity") or {}

    nightly_price = _safe_float(
        price.get("nightlyPrice")
    )

    total_price = _safe_float(
        price.get("totalPrice")
    )

    image_url = _get_hotel_image(hotel)

    return {
        # Basic information
        "id": hotel.get("id"),

        "name": hotel.get(
            "name",
            "Unknown Hotel",
        ),

        # Location
        "address": (
            f"{location.get('city', '')}, "
            f"{location.get('country', '')}"
        ).strip(", "),

        "latitude": _safe_float(
            location.get("lat")
        ),

        "longitude": _safe_float(
            location.get("lng")
        ),

        # Price
        "price_per_night": nightly_price,

        "total_price": total_price,

        "currency": price.get(
            "currency",
            "USD",
        ),

        "nights": price.get(
            "nights"
        ),

        # Rating
        "rating": _safe_float(
            hotel.get("guestRating")
        ),

        "rating_scale": hotel.get(
            "ratingScale"
        ),

        "review_count": hotel.get(
            "reviewCount",
            0,
        ),

        "star_rating": hotel.get(
            "starRating"
        ),

        # Property
        "property_type": hotel.get(
            "propertyType"
        ),

        "bedrooms": hotel.get(
            "bedrooms"
        ),

        "bathrooms": hotel.get(
            "bathrooms"
        ),

        "max_occupancy": hotel.get(
            "maxOccupancy"
        ),

        # Amenities
        "amenities": hotel.get(
            "amenities",
            [],
        ),

        # Platform
        "platform": hotel.get(
            "platform"
        ),

        "platform_listing_id": hotel.get(
            "platformListingId"
        ),

        # Booking URL
        "website": (
            identity.get("canonicalUrl")
            or hotel.get("url")
        ),

        # ⭐ HOTEL IMAGE
        "image_url": image_url,

        # Host
        "host": hotel.get(
            "host"
        ),

        # Source
        "source": "stayingapi",
    }


async def search_hotels(
    destination: str,
    latitude: float,
    longitude: float,
    check_in: str,
    check_out: str,
    travelers: int = 2,
) -> list[dict[str, Any]]:

    print(
        "\n[hotels] ========================================"
    )

    print(
        "[hotels] HOTEL SEARCH - STAYINGAPI"
    )

    print(
        f"[hotels] Destination: {destination}"
    )

    print(
        f"[hotels] Latitude: {latitude}"
    )

    print(
        f"[hotels] Longitude: {longitude}"
    )

    print(
        f"[hotels] Check-in: {check_in}"
    )

    print(
        f"[hotels] Check-out: {check_out}"
    )

    print(
        f"[hotels] Adults: {travelers}"
    )

    # ============================================================
    # GET API KEY
    # ============================================================

    api_key = getattr(
        settings,
        "staying_api_key",
        None,
    )

    if not api_key:

        print(
            "[hotels] ERROR: STAYING_API_KEY is missing"
        )

        return []

    # ============================================================
    # STAYING API PARAMETERS
    # ============================================================

    params = {
        "location": f"{latitude},{longitude}",
        "checkIn": check_in,
        "checkOut": check_out,
        "adults": travelers,
        "rooms": 1,
        "limit": 20,
        "sort": "recommended",
        "currency": "INR",
    }

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    print(
        f"[hotels] URL: {STAYING_API_URL}"
    )

    print(
        f"[hotels] Params: {params}"
    )

    # ============================================================
    # API REQUEST
    # ============================================================

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                STAYING_API_URL,
                params=params,
                headers=headers,
            )

            print(
                f"[hotels] HTTP status: "
                f"{response.status_code}"
            )

            # ====================================================
            # API ERROR
            # ====================================================

            if response.status_code != 200:

                print(
                    f"[hotels] API ERROR: "
                    f"{response.text}"
                )

                return []

            # ====================================================
            # PARSE JSON
            # ====================================================

            result = response.json()

            hotels_data = result.get(
                "data",
                [],
            )

            if not isinstance(
                hotels_data,
                list,
            ):

                print(
                    "[hotels] ERROR: "
                    "'data' is not a list"
                )

                return []

            # ====================================================
            # NORMALIZE HOTELS
            # ====================================================

            hotels: list[
                dict[str, Any]
            ] = []

            for hotel in hotels_data:

                if not isinstance(
                    hotel,
                    dict,
                ):
                    continue

                # IMPORTANT:
                # Only ONE argument
                normalized_hotel = _normalize_hotel(
                    hotel
                )

                hotels.append(
                    normalized_hotel
                )

            # ====================================================
            # METADATA
            # ====================================================

            meta = result.get(
                "meta"
            ) or {}

            print(
                f"[hotels] Hotels received: "
                f"{len(hotels)}"
            )

            print(
                f"[hotels] Platforms: "
                f"{meta.get('platforms')}"
            )

            print(
                f"[hotels] Cached: "
                f"{meta.get('cached')}"
            )

            print(
                f"[hotels] Partial: "
                f"{meta.get('partial')}"
            )

            # ====================================================
            # DEBUG IMAGE
            # ====================================================

            for hotel in hotels:

                print(
                    f"[hotels] Hotel: "
                    f"{hotel.get('name')}"
                )

                print(
                    f"[hotels] Image: "
                    f"{hotel.get('image_url')}"
                )

            return hotels

    # ============================================================
    # HTTP ERROR
    # ============================================================

    except httpx.HTTPError as exc:

        print(
            f"[hotels] HTTP request error: "
            f"{exc}"
        )

        return []

    # ============================================================
    # UNEXPECTED ERROR
    # ============================================================

    except Exception as exc:

        print(
            f"[hotels] Unexpected error: "
            f"{exc}"
        )

        return []