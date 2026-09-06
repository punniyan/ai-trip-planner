import uuid

from fastapi import APIRouter

from app.schemas import (
    TripRequest,
    TripResponse,
)

from app.agent.agent import (
    run_trip_agent,
)

from app.database import (
    trips_collection,
)

from app.agent.memory import (
    get_conversation,
    save_conversation,
    save_message,
)


router = APIRouter(
    prefix="/api/trip",
    tags=["Chat"],
)


@router.post(
    "/chat",
    response_model=TripResponse,
)
async def chat(
    request: TripRequest,
):

    # ========================================================
    # CONVERSATION ID
    # ========================================================

    conversation_id = (
        request.conversation_id
        or str(uuid.uuid4())
    )

    print("\n======================================")
    print("CONVERSATION ID:", conversation_id)
    print("USER MESSAGE:", request.message)
    print("======================================\n")

    # ========================================================
    # LOAD PREVIOUS CONVERSATION
    # ========================================================

    conversation = get_conversation(
        conversation_id
    )

    previous_trip = None

    if conversation:

        previous_trip = (
            conversation.get("trip")
        )

    print(
        "PREVIOUS TRIP:",
        previous_trip,
    )

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    save_message(
        conversation_id,
        "user",
        request.message,
    )

    try:

        # ====================================================
        # RUN AGENT
        # ====================================================

        result = await run_trip_agent(
            request.message,
            previous_trip,
        )

        trip = result.get(
            "trip"
        )

        # ====================================================
        # SAVE TRIP TO MONGODB
        # ====================================================

        if trip and trip.get("trip_id"):

            trips_collection.update_one(
                {
                    "trip_id": trip["trip_id"]
                },
                {
                    "$set": trip
                },
                upsert=True,
            )

        # ====================================================
        # SAVE CONVERSATION
        # ====================================================

        save_conversation(
            conversation_id,
            trip or {},
            request.user_id,
        )

        # ====================================================
        # ASSISTANT MESSAGE
        # ====================================================

        assistant_message = (
            result.get(
                "message",
                "",
            )
        )

        save_message(
            conversation_id,
            "assistant",
            assistant_message,
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "conversation_id": (
                conversation_id
            ),

            "message": assistant_message,

            "trip": trip,

            "missing_fields": (
                result.get(
                    "missing_fields",
                    [],
                )
            ),

            "requires_date": (
                result.get(
                    "requires_date",
                    False,
                )
            ),

            "success": True,

            "error": None,
        }

    except Exception as exc:

        print(
            "CHAT ERROR:",
            exc,
        )

        return {

            "conversation_id": (
                conversation_id
            ),

            "message": (
                "Unable to create "
                "the trip right now."
            ),

            "trip": previous_trip,

            "missing_fields": [],

            "requires_date": False,

            "success": False,

            "error": str(exc),
        }