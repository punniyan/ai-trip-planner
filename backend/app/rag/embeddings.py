from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
)

from app.config import settings


def get_embeddings():

    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is required for RAG embeddings."
        )

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.google_api_key,
    )