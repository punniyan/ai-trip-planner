from typing import Any, TypedDict


class TripState(TypedDict, total=False):

    message: str

    conversation_id: str

    user_id: str | None

    trip: dict[str, Any]

    extracted: dict[str, Any]

    missing_fields: list[str]

    rag_context: str

    flights: list[dict]

    hotels: list[dict]

    places: list[dict]

    restaurants: list[dict]

    weather: list[dict]

    itinerary: list[dict]

    response_message: str