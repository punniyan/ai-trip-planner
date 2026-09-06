import httpx

from app.config import settings


async def get_route(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
) -> dict:

    if not settings.google_maps_api_key:
        return {}

    url = (
        "https://maps.googleapis.com/maps/api/"
        "directions/json"
    )

    params = {
        "origin": (
            f"{origin_lat},{origin_lon}"
        ),
        "destination": (
            f"{destination_lat},{destination_lon}"
        ),
        "mode": "driving",
        "key": settings.google_maps_api_key,
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()