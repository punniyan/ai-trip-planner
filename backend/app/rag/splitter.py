from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: list[Any],
) -> list[Any]:

    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    return splitter.split_documents(
        documents
    )