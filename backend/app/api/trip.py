# app/api/trip.py

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.agent import run_trip_agent


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/trip",
    tags=["Trip"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class TripChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    previous_trip: dict[str, Any] | None = None


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post("/chat")
async def trip_chat(
    request: TripChatRequest,
):
    result = await run_trip_agent(
        user_message=request.message,
        previous_trip=request.previous_trip,
        conversation_id=request.conversation_id,
    )

    return {
        "conversation_id": request.conversation_id
        or result.get("conversation_id"),
        **result,
    }