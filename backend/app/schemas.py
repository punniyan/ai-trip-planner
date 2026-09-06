from typing import Any

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User trip request",
    )

    conversation_id: str | None = None

    user_id: str | None = None


class TripResponse(BaseModel):
    conversation_id: str

    message: str

    trip: dict[str, Any] | None = None

    missing_fields: list[str] = Field(
        default_factory=list
    )

    requires_date: bool = False

    success: bool = True

    error: str | None = None