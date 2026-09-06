# app/rag/retriever.py

import re
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from app.rag.splitter import split_documents


# ============================================================
# RAG DATA DIRECTORY
# ============================================================

RAG_DATA_DIR = (
    Path(__file__).resolve().parent / "data"
)


# ============================================================
# LOAD DOCUMENTS
# ============================================================

def load_rag_documents() -> list[Document]:

    documents = []

    if not RAG_DATA_DIR.exists():

        print(
            "RAG data directory does not exist:",
            RAG_DATA_DIR,
        )

        return documents

    for file_path in RAG_DATA_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in {
            ".txt",
            ".md",
        }:
            continue

        try:

            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                continue

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": file_path.name,
                    },
                )
            )

            print(
                "RAG document loaded:",
                file_path.name,
            )

        except Exception as error:

            print(
                "RAG document loading error:",
                file_path,
                error,
            )

    print(
        "TOTAL RAG DOCUMENTS:",
        len(documents),
    )

    return documents


# ============================================================
# NORMALIZE WORDS
# ============================================================

def _normalize_words(
    text: str,
) -> set[str]:

    if not text:
        return set()

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if len(word) > 2
    }


# ============================================================
# EXTRACT DESTINATION
# ============================================================

def _extract_destination(
    query: str,
) -> str:

    if not query:
        return ""

    text = " ".join(
        query.strip().split()
    )

    # --------------------------------------------------------
    # Example:
    #
    # from Chennai to Dubai for 2 travelers
    #
    # => Dubai
    # --------------------------------------------------------

    patterns = [

        r"\bto\s+([A-Za-z][A-Za-z .'-]*?)(?=\s+\bfor\b|\s+\bfrom\b|\s+\bon\b|\s+\bbetween\b|\s+\bwith\b|\s+\bmy\b|\s+\bbudget\b|\s+\binclude\b|[.,]|$)",

        r"\bdestination\s*[:=]\s*([A-Za-z][A-Za-z .'-]*?)(?=\s+\bfor\b|\s+\bfrom\b|\s+\bon\b|\s+\bbetween\b|\s+\bwith\b|\s+\bmy\b|\s+\bbudget\b|\s+\binclude\b|[.,]|$)",

        r"\btrip\s+to\s+([A-Za-z][A-Za-z .'-]*?)(?=\s+\bfor\b|\s+\bfrom\b|\s+\bon\b|\s+\bbetween\b|\s+\bwith\b|\s+\bmy\b|\s+\bbudget\b|\s+\binclude\b|[.,]|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        value = match.group(
            1
        ).strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        if value:
            return value

    # --------------------------------------------------------
    # Known destination fallback
    # --------------------------------------------------------

    known_destinations = [
        "dubai",
        "abu dhabi",
        "sharjah",
        "singapore",
        "bangkok",
        "paris",
        "london",
        "tokyo",
        "kuala lumpur",
        "bali",
        "maldives",
        "new york",
        "los angeles",
    ]

    text_lower = text.lower()

    for destination in known_destinations:

        if re.search(
            rf"\b{re.escape(destination)}\b",
            text_lower,
        ):

            return destination

    return ""


# ============================================================
# DESTINATION IN CONTENT
# ============================================================

def _destination_matches(
    destination: str,
    content: str,
    source: str,
) -> bool:

    if not destination:
        return False

    destination_normalized = (
        destination.strip().lower()
    )

    content_lower = content.lower()
    source_lower = source.lower()

    # --------------------------------------------------------
    # Direct phrase match
    # --------------------------------------------------------

    if destination_normalized in content_lower:
        return True

    if destination_normalized in source_lower:
        return True

    # --------------------------------------------------------
    # Word based match
    # Useful for "New York"
    # --------------------------------------------------------

    destination_words = (
        _normalize_words(
            destination
        )
    )

    if not destination_words:
        return False

    content_words = _normalize_words(
        content
    )

    return destination_words.issubset(
        content_words
    )


# ============================================================
# REMOVE OTHER DESTINATION SECTIONS
# ============================================================

def _extract_destination_section(
    content: str,
    destination: str,
) -> str:

    if not content or not destination:
        return content

    destination_normalized = (
        destination.strip().lower()
    )

    # --------------------------------------------------------
    # Split common markdown/plain-text headings.
    #
    # Example:
    #
    # DUBAI
    # ...
    # SINGAPORE
    # ...
    # --------------------------------------------------------

    sections = re.split(
        r"\n\s*(?=[A-Z][A-Z0-9 &'-]{2,}\s*$)",
        content,
        flags=re.MULTILINE,
    )

    if len(sections) <= 1:
        return content

    matching_sections = []

    for section in sections:

        section_lower = section.lower()

        if destination_normalized in section_lower:

            matching_sections.append(
                section.strip()
            )

    if matching_sections:

        return "\n\n".join(
            matching_sections
        )

    return ""


# ============================================================
# RETRIEVE CONTEXT
# ============================================================

def retrieve_context(
    query: str,
    documents: list[Any] | None = None,
    top_k: int = 5,
) -> str:

    if not query:
        return ""

    if documents is None:
        documents = load_rag_documents()

    if not documents:

        print(
            "RAG: No documents available."
        )

        return ""

    destination = _extract_destination(
        query
    )

    print(
        "RAG QUERY:",
        query,
    )

    print(
        "RAG DESTINATION:",
        destination,
    )

    try:

        chunks = split_documents(
            documents
        )

        if not chunks:
            return ""

        query_words = _normalize_words(
            query
        )

        scored_chunks = []

        for document in chunks:

            content = getattr(
                document,
                "page_content",
                "",
            )

            if not content:
                continue

            metadata = getattr(
                document,
                "metadata",
                {},
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            source = str(
                metadata.get(
                    "source",
                    "",
                )
            )

            # ------------------------------------------------
            # DESTINATION FILTER
            # ------------------------------------------------

            destination_match = (
                _destination_matches(
                    destination,
                    content,
                    source,
                )
            )

            # ------------------------------------------------
            # If destination exists,
            # unrelated destination chunks
            # must be completely ignored.
            # ------------------------------------------------

            if destination:

                if not destination_match:
                    continue

            content_words = _normalize_words(
                content
            )

            word_score = len(
                query_words.intersection(
                    content_words
                )
            )

            # Destination gets strong priority.
            if destination_match:

                score = (
                    100
                    + word_score
                )

            else:

                score = word_score

            if score > 0:

                scored_chunks.append(
                    (
                        score,
                        content,
                        source,
                    )
                )

        # ----------------------------------------------------
        # Sort highest score first
        # ----------------------------------------------------

        scored_chunks.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        selected = []

        seen_content: set[str] = set()

        for (
            score,
            content,
            source,
        ) in scored_chunks:

            if content in seen_content:
                continue

            seen_content.add(
                content
            )

            # -----------------------------------------------
            # Extra destination section cleanup
            # -----------------------------------------------

            cleaned_content = (
                _extract_destination_section(
                    content,
                    destination,
                )
            )

            if cleaned_content:
                content = cleaned_content

            selected.append(
                content
            )

            if len(selected) >= top_k:
                break

        result = "\n\n".join(
            selected
        )

        print(
            "RAG MATCHED CHUNKS:",
            len(selected),
        )

        print(
            "RAG CONTEXT LENGTH:",
            len(result),
        )

        return result

    except Exception as error:

        print(
            "RAG retrieval error:",
            error,
        )

        return ""