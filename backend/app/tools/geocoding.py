from typing import Any

import httpx

from app.config import settings


# ============================================================
# GEOCODE DESTINATION
# ============================================================

async def geocode_destination(
    destination: str,
) -> dict[str, Any] | None:

    destination = destination.strip()

    if not destination:
        return None

    # ========================================================
    # GEOAPIFY
    # ========================================================

    if settings.geoapify_api_key:

        try:

            url = (
                "https://api.geoapify.com/v1/"
                "geocode/search"
            )

            params = {
                "text": destination,
                "limit": 1,
                "apiKey": settings.geoapify_api_key,
            }

            print(
                f"[geocoding] Searching destination: "
                f"{destination}"
            )

            async with httpx.AsyncClient(
                timeout=20.0
            ) as client:

                response = await client.get(
                    url,
                    params=params,
                )

                print(
                    "[geocoding] Geoapify status:",
                    response.status_code,
                )

                response.raise_for_status()

                data = response.json()

            features = data.get(
                "features",
                [],
            )

            if features:

                feature = features[0]

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
                    isinstance(coordinates, list)
                    and len(coordinates) >= 2
                ):

                    longitude = float(
                        coordinates[0]
                    )

                    latitude = float(
                        coordinates[1]
                    )

                    result = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "name": properties.get(
                            "name",
                            destination,
                        ),
                        "country": properties.get(
                            "country"
                        ),
                        "formatted": properties.get(
                            "formatted",
                            destination,
                        ),
                        "source": "geoapify",
                    }

                    print(
                        "[geocoding] SUCCESS:"
                    )

                    print(
                        f"[geocoding] "
                        f"Latitude: {latitude}"
                    )

                    print(
                        f"[geocoding] "
                        f"Longitude: {longitude}"
                    )

                    print(
                        f"[geocoding] "
                        f"Formatted: "
                        f"{result['formatted']}"
                    )

                    return result

        except Exception as error:

            print(
                "[geocoding] Geoapify error:",
                repr(error),
            )

    # ========================================================
    # NOMINATIM FALLBACK
    # ========================================================

    try:

        print(
            "[geocoding] Trying Nominatim fallback..."
        )

        params = {
            "q": destination,
            "format": "json",
            "limit": 1,
        }

        headers = {
            "User-Agent": "AI-Trip-Planner/1.0"
        }

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            response = await client.get(
                settings.nominatim_url,
                params=params,
                headers=headers,
            )

            print(
                "[geocoding] Nominatim status:",
                response.status_code,
            )

            response.raise_for_status()

            data = response.json()

        if data:

            item = data[0]

            latitude = float(
                item["lat"]
            )

            longitude = float(
                item["lon"]
            )

            result = {
                "latitude": latitude,
                "longitude": longitude,
                "name": item.get(
                    "display_name",
                    destination,
                ),
                "country": None,
                "formatted": item.get(
                    "display_name",
                    destination,
                ),
                "source": "nominatim",
            }

            print(
                "[geocoding] Nominatim SUCCESS:"
            )

            print(
                f"[geocoding] "
                f"Latitude: {latitude}"
            )

            print(
                f"[geocoding] "
                f"Longitude: {longitude}"
            )

            return result

    except Exception as error:

        print(
            "[geocoding] Nominatim error:",
            repr(error),
        )

    # ========================================================
    # NOTHING FOUND
    # ========================================================

    print(
        "[geocoding] ERROR: "
        "Could not geocode destination"
    )

    return None


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

async def geocode_location(
    location: str,
) -> dict[str, Any] | None:

    return await geocode_destination(
        location
    )