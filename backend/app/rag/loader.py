from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
)


DATA_DIR = Path(
    "data/destinations"
)


def load_documents():

    documents = []

    if not DATA_DIR.exists():
        return documents

    for file_path in DATA_DIR.glob("*.txt"):

        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
        )

        documents.extend(
            loader.load()
        )

    return documents