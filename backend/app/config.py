# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ============================================================
    # GEMINI
    # ============================================================
    google_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # ============================================================
    # GEOAPIFY
    # ============================================================
    geoapify_api_key: str = ""
    geoapify_url: str = "https://api.geoapify.com/v2/places"

    # ============================================================
    # STAYINGAPI
    # Used for hotel data
    # Sandbox / Demo inventory - No booking
    # ============================================================

    staying_api_key: str = ""
    staying_api_url: str = ""

    # ============================================================
    # WEATHER
    # ============================================================
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"

    # ============================================================
    # CURRENCY
    # ============================================================
    currency_api_url: str = "https://api.frankfurter.app"
    exchange_rate_api_url: str = "https://open.er-api.com/v6/latest"

    # ========================================================
    # SERPAPI - GOOGLE FLIGHTS
    # ========================================================

    serpapi_api_key: str | None = None

    serpapi_base_url: str = (
        "https://serpapi.com/search.json"
    )

    # ============================================================
    # GEOCODING
    # ============================================================
    nominatim_url: str = (
        "https://nominatim.openstreetmap.org/search"
    )

    overpass_url: str = (
        "https://overpass-api.de/api/interpreter"
    )

    # ============================================================
    # CORS
    # ============================================================
    cors_origins: str = "http://localhost:5173"

    # ============================================================
    # SETTINGS CONFIG
    # ============================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ============================================================
# SETTINGS INSTANCE
# ============================================================
settings = Settings()