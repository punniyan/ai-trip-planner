from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import settings


client = MongoClient(
    settings.mongo_uri,
    serverSelectionTimeoutMS=5000,
)

db = client[settings.mongo_db_name]

trips_collection = db["trips"]

conversations_collection = db["conversations"]

messages_collection = db["messages"]


def check_database() -> bool:
    """
    Check whether MongoDB is reachable.
    """
    try:
        client.admin.command("ping")
        return True

    except PyMongoError:
        return False


def close_database() -> None:
    """
    Close MongoDB connection.
    """
    client.close()