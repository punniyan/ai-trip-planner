from datetime import date
from typing import Any

import httpx

from app.config import settings


WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _safe_float(
    value: Any,
) -> float | None:

    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _safe_int(
    value: Any,
) -> int | None:

    try:
        if value is None:
            return None

        return int(value)

    except (TypeError, ValueError):
        return None


async def get_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:

    print("\n[weather] ========================================")
    print("[weather] WEATHER SEARCH")
    print(f"[weather] Latitude: {latitude}")
    print(f"[weather] Longitude: {longitude}")
    print(f"[weather] Start date: {start_date}")
    print(f"[weather] End date: {end_date}")

    url = getattr(
        settings,
        "open_meteo_url",
        "https://api.open-meteo.com/v1/forecast",
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "weather_code,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto",
    }

    print("[weather] Request:", url)

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

            print(
                f"[weather] HTTP status: "
                f"{response.status_code}"
            )

            if response.status_code != 200:

                print(
                    "[weather] ERROR:",
                    response.text[:1000],
                )

                return []

            data = response.json()

            daily = (
                data.get("daily", {})
                or {}
            )

            dates = daily.get("time", []) or []

            max_temps = (
                daily.get(
                    "temperature_2m_max",
                    [],
                )
                or []
            )

            min_temps = (
                daily.get(
                    "temperature_2m_min",
                    [],
                )
                or []
            )

            weather_codes = (
                daily.get(
                    "weather_code",
                    [],
                )
                or []
            )

            precipitation = (
                daily.get(
                    "precipitation_sum",
                    [],
                )
                or []
            )

            wind_speed = (
                daily.get(
                    "wind_speed_10m_max",
                    [],
                )
                or []
            )

            results: list[
                dict[str, Any]
            ] = []

            for index, weather_date in enumerate(
                dates
            ):

                code = (
                    weather_codes[index]
                    if index < len(weather_codes)
                    else None
                )

                weather_item = {
                    "date": weather_date,
                    "temperature_max": (
                        _safe_float(
                            max_temps[index]
                        )
                        if index < len(max_temps)
                        else None
                    ),
                    "temperature_min": (
                        _safe_float(
                            min_temps[index]
                        )
                        if index < len(min_temps)
                        else None
                    ),
                    "weather_code": code,
                    "description": (
                        WEATHER_CODE_MAP.get(
                            _safe_int(code),
                            "Unknown",
                        )
                    ),
                    "precipitation": (
                        _safe_float(
                            precipitation[index]
                        )
                        if index < len(precipitation)
                        else None
                    ),
                    "wind_speed": (
                        _safe_float(
                            wind_speed[index]
                        )
                        if index < len(wind_speed)
                        else None
                    ),
                    "latitude": latitude,
                    "longitude": longitude,
                    "source": "open-meteo",
                }

                results.append(weather_item)

            print(
                f"[weather] Final results: "
                f"{len(results)}"
            )

            return results

    except Exception as exc:

        print(
            "[weather] Request error:",
            repr(exc),
        )

        return []