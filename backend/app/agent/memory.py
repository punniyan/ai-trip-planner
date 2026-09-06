from datetime import datetime
from typing import Any

from app.database import conversations_collection


# ============================================================
# GET CONVERSATION
# ============================================================

def get_conversation(
    conversation_id: str,
) -> dict[str, Any] | None:

    if not conversation_id:
        return None

    conversation = conversations_collection.find_one(
        {
            "conversation_id": conversation_id
        }
    )

    return conversation


# ============================================================
# SAVE CONVERSATION
# ============================================================

def save_conversation(
    conversation_id: str,
    trip: dict[str, Any],
    user_id: str | None = None,
) -> None:

    if not conversation_id:
        return

    now = datetime.utcnow()

    conversations_collection.update_one(
        {
            "conversation_id": conversation_id
        },
        {
            "$set": {
                "conversation_id": conversation_id,
                "trip": trip,
                "user_id": user_id,
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )


# ============================================================
# SAVE MESSAGE
# ============================================================

def save_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:

    if not conversation_id:
        return

    conversations_collection.update_one(
        {
            "conversation_id": conversation_id
        },
        {
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "created_at": datetime.utcnow(),
                }
            }
        },
        upsert=True,
    )