from pathlib import Path

from langchain_community.vectorstores import (
    FAISS,
)

from app.rag.embeddings import get_embeddings
from app.rag.loader import load_documents
from app.rag.splitter import split_documents


VECTOR_PATH = Path(
    "data/faiss_index"
)


def build_vectorstore():

    documents = load_documents()

    if not documents:
        return None

    chunks = split_documents(
        documents
    )

    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings,
    )

    VECTOR_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vectorstore.save_local(
        str(VECTOR_PATH)
    )

    return vectorstore


def get_vectorstore():

    embeddings = get_embeddings()

    index_file = (
        VECTOR_PATH / "index.faiss"
    )

    if index_file.exists():

        return FAISS.load_local(
            str(VECTOR_PATH),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    return build_vectorstore()