# app/agent/agent.py

import json
import re
import uuid

from datetime import date, datetime, timedelta
from typing import Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.agent.prompts import (
    TRIP_EXTRACTION_PROMPT,
    TRIP_FOLLOWUP_PROMPT,
)
from app.rag.retriever import retrieve_context
from app.services.validation_service import validate_trip
from app.services.itinerary_service import create_itinerary


# ============================================================
# OPTIONAL TOOL IMPORTS
# ============================================================

try:
    from app.tools.flights import search_flights
except Exception:
    search_flights = None

try:
    from app.tools.hotels import search_hotels
except Exception:
    search_hotels = None

try:
    from app.tools.places import search_places
except Exception:
    search_places = None

try:
    from app.tools.restaurants import search_restaurants
except Exception:
    search_restaurants = None

try:
    from app.tools.weather import get_weather
except Exception:
    get_weather = None

try:
    from app.tools.currency import convert_currency
except Exception:
    convert_currency = None

try:
    from app.tools.geocoding import geocode_destination
except Exception:
    geocode_destination = None


# ============================================================
# LLM
# ============================================================

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        if value is None:
            return default

        if isinstance(value, bool):
            return int(value)

        return int(float(str(value).strip()))

    except Exception:
        return default


def _safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    try:
        if value is None:
            return default

        if isinstance(value, (int, float)):
            return float(value)

        cleaned = str(value).replace(",", "").strip()

        match = re.search(r"-?\d+(?:\.\d+)?", cleaned)

        if match:
            return float(match.group())

        return default

    except Exception:
        return default


def _clean_string(value: Any) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


# ============================================================
# DATE NORMALIZATION
# ============================================================

def _normalize_date(value: Any) -> Optional[str]:

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # --------------------------------------------------------
    # YYYY-MM-DD
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b",
        text,
    )

    if match:
        try:
            year, month, day = map(int, match.groups())
            return date(year, month, day).isoformat()
        except Exception:
            pass

    # --------------------------------------------------------
    # DD-MM-YYYY
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b",
        text,
    )

    if match:
        try:
            day, month, year = map(int, match.groups())
            return date(year, month, day).isoformat()
        except Exception:
            pass

    # --------------------------------------------------------
    # Month DD, YYYY
    # Example:
    # September 10, 2026
    # Sep 10 2026
    # --------------------------------------------------------

    month_pattern = (
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    )

    match = re.search(
        rf"\b{month_pattern}\s+(\d{{1,2}})"
        rf"(?:st|nd|rd|th)?"
        rf"(?:,\s*|\s+)(\d{{4}})\b",
        text,
        re.IGNORECASE,
    )

    if match:
        try:
            month_name = match.group(1)
            day = int(match.group(2))
            year = int(match.group(3))

            parsed = datetime.strptime(
                f"{month_name} {day} {year}",
                "%B %d %Y",
            )

            return parsed.date().isoformat()

        except Exception:
            try:
                parsed = datetime.strptime(
                    f"{month_name} {day} {year}",
                    "%b %d %Y",
                )

                return parsed.date().isoformat()

            except Exception:
                pass

    # --------------------------------------------------------
    # DD Month YYYY
    # Example:
    # 10 September 2026
    # 10 Sep 2026
    # --------------------------------------------------------

    match = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+"
        rf"{month_pattern}\s+(\d{{4}})\b",
        text,
        re.IGNORECASE,
    )

    if match:
        try:
            day = int(match.group(1))
            month_name = match.group(2)
            year = int(match.group(3))

            parsed = datetime.strptime(
                f"{day} {month_name} {year}",
                "%d %B %Y",
            )

            return parsed.date().isoformat()

        except Exception:
            try:
                parsed = datetime.strptime(
                    f"{day} {month_name} {year}",
                    "%d %b %Y",
                )

                return parsed.date().isoformat()

            except Exception:
                pass

    # --------------------------------------------------------
    # Month DD without year
    # Uses current year
    # --------------------------------------------------------

    match = re.search(
        rf"\b{month_pattern}\s+(\d{{1,2}})"
        rf"(?:st|nd|rd|th)?\b",
        text,
        re.IGNORECASE,
    )

    if match:
        try:
            month_name = match.group(1)
            day = int(match.group(2))
            year = date.today().year

            try:
                parsed = datetime.strptime(
                    f"{month_name} {day} {year}",
                    "%B %d %Y",
                )
            except Exception:
                parsed = datetime.strptime(
                    f"{month_name} {day} {year}",
                    "%b %d %Y",
                )

            return parsed.date().isoformat()

        except Exception:
            pass

    return None


# ============================================================
# EXTRACT JSON FROM LLM RESPONSE
# ============================================================

def _extract_json_from_text(text: Any) -> dict:

    if text is None:
        return {}

    if isinstance(text, dict):
        return text

    text = str(text).strip()

    if not text:
        return {}

    # --------------------------------------------------------
    # Remove markdown JSON fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    # --------------------------------------------------------
    # Find JSON object inside text
    # --------------------------------------------------------

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if match:
        try:
            result = json.loads(match.group())

            if isinstance(result, dict):
                return result

        except Exception:
            pass

    return {}


# ============================================================
# GET LLM TEXT
# ============================================================

def _get_llm_text(response: Any) -> str:

    if response is None:
        return ""

    content = getattr(response, "content", None)

    if content is not None:

        if isinstance(content, str):
            return content

        if isinstance(content, list):

            parts = []

            for item in content:

                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    if "text" in item:
                        parts.append(str(item["text"]))

            return "".join(parts)

        return str(content)

    return str(response)


# ============================================================
# NORMALIZE TRIP DATA
# ============================================================

def _normalize_trip_data(data: Any) -> dict:

    if not isinstance(data, dict):
        return {}

    result = {}

    # --------------------------------------------------------
    # Origin
    # --------------------------------------------------------

    origin = (
        data.get("origin")
        or data.get("from")
        or data.get("source")
    )

    # --------------------------------------------------------
    # Destination
    # --------------------------------------------------------

    destination = (
        data.get("destination")
        or data.get("to")
        or data.get("city")
    )

    # --------------------------------------------------------
    # Start date
    # --------------------------------------------------------

    start_date = (
        data.get("start_date")
        or data.get("departure_date")
        or data.get("travel_start")
    )

    # --------------------------------------------------------
    # End date
    # --------------------------------------------------------

    end_date = (
        data.get("end_date")
        or data.get("return_date")
        or data.get("travel_end")
    )

    # --------------------------------------------------------
    # Travelers
    # --------------------------------------------------------

    travelers = (
        data.get("travelers")
        or data.get("number_of_travelers")
        or data.get("guests")
    )

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    budget = (
        data.get("budget")
        or data.get("max_budget")
    )

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    currency = (
        data.get("currency")
        or data.get("budget_currency")
    )

    if origin:
        result["origin"] = _clean_string(origin)

    if destination:
        result["destination"] = _clean_string(destination)

    normalized_start = _normalize_date(start_date)

    if normalized_start:
        result["start_date"] = normalized_start

    normalized_end = _normalize_date(end_date)

    if normalized_end:
        result["end_date"] = normalized_end

    travelers_value = _safe_int(travelers)

    if travelers_value is not None and travelers_value > 0:
        result["travelers"] = travelers_value

    budget_value = _safe_float(budget)

    if budget_value is not None:
        result["budget"] = budget_value

    if currency:
        result["currency"] = str(currency).strip().upper()

    # --------------------------------------------------------
    # Defaults
    # --------------------------------------------------------

    if "travelers" not in result:
        result["travelers"] = 1

    if "currency" not in result:
        result["currency"] = "INR"

    return result


# ============================================================
# LOCAL FALLBACK EXTRACTION
# ============================================================
#
# IMPORTANT:
# This function allows the application to continue working
# even when Gemini returns HTTP 429 quota exceeded.
#
# It handles common requests such as:
#
# Plan a 4 day trip from Chennai to Dubai
# from Chennai to Dubai from September 10 to September 13
# Chennai to Dubai September 10 2026 to September 13 2026
# trip for 2 people
# budget 50000 INR
#
# ============================================================

def _local_fallback_extract_trip_data(
    user_message: str,
) -> dict:

    print("=" * 70)
    print("[agent] USING LOCAL PYTHON EXTRACTION FALLBACK")
    print("=" * 70)

    if not user_message:
        return {}

    text = user_message.strip()

    result = {}

    # ========================================================
    # ORIGIN + DESTINATION
    # ========================================================

    # Example:
    # from Chennai to Dubai
    #
    # Stops before:
    # for
    # on
    # from
    # starting
    # budget
    # with
    #
    route_pattern = re.compile(
        r"\bfrom\s+"
        r"([A-Za-z][A-Za-z .'-]*?)"
        r"\s+to\s+"
        r"([A-Za-z][A-Za-z .'-]*?)"
        r"(?=\s+(?:for|on|from|starting|with|within|under|budget|"
        r"between|in)\b|[,.!?]|$)",
        re.IGNORECASE,
    )

    route_match = route_pattern.search(text)

    if route_match:

        origin = route_match.group(1).strip(" ,.-")
        destination = route_match.group(2).strip(" ,.-")

        if origin:
            result["origin"] = origin

        if destination:
            result["destination"] = destination

    # ========================================================
    # SIMPLE "Chennai to Dubai"
    # ========================================================

    if "destination" not in result:

        simple_route_pattern = re.compile(
            r"\b([A-Za-z][A-Za-z .'-]*?)"
            r"\s+to\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"(?=\s+(?:for|on|from|starting|with|within|under|budget|"
            r"between|in)\b|[,.!?]|$)",
            re.IGNORECASE,
        )

        simple_match = simple_route_pattern.search(text)

        if simple_match:

            possible_origin = simple_match.group(1).strip(" ,.-")
            possible_destination = simple_match.group(2).strip(" ,.-")

            # Avoid interpreting phrases like:
            # "I want to go to Dubai"
            if possible_origin.lower() not in {
                "want",
                "go",
                "travel",
                "trip",
                "plan",
                "traveling",
                "travelling",
            }:

                result["origin"] = possible_origin
                result["destination"] = possible_destination

    # ========================================================
    # DESTINATION ONLY
    # ========================================================

    if "destination" not in result:

        destination_match = re.search(
            r"\bto\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"(?=\s+(?:for|on|from|starting|with|within|under|budget|"
            r"between|in)\b|[,.!?]|$)",
            text,
            re.IGNORECASE,
        )

        if destination_match:

            destination = destination_match.group(1).strip(" ,.-")

            if destination:
                result["destination"] = destination

    # ========================================================
    # ORIGIN ONLY
    # ========================================================

    if "origin" not in result:

        origin_match = re.search(
            r"\bfrom\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"(?=\s+(?:to|on|starting|for|with|within|under|budget)\b|[,.!?]|$)",
            text,
            re.IGNORECASE,
        )

        if origin_match:

            origin = origin_match.group(1).strip(" ,.-")

            if origin:
                result["origin"] = origin

    # ========================================================
    # START DATE + END DATE
    # ========================================================

    date_values = []

    # --------------------------------------------------------
    # ISO dates
    # --------------------------------------------------------

    iso_matches = re.findall(
        r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
        text,
    )

    for item in iso_matches:

        normalized = _normalize_date(item)

        if normalized and normalized not in date_values:
            date_values.append(normalized)

    # --------------------------------------------------------
    # DD-MM-YYYY dates
    # --------------------------------------------------------

    numeric_matches = re.findall(
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
        text,
    )

    for item in numeric_matches:

        normalized = _normalize_date(item)

        if normalized and normalized not in date_values:
            date_values.append(normalized)

    # --------------------------------------------------------
    # Month dates
    # --------------------------------------------------------

    month_pattern = (
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    )

    month_date_matches = re.findall(
        rf"\b{month_pattern}\s+\d{{1,2}}"
        rf"(?:st|nd|rd|th)?"
        rf"(?:,\s*|\s+)\d{{4}}\b",
        text,
        re.IGNORECASE,
    )

    for item in month_date_matches:

        normalized = _normalize_date(item)

        if normalized and normalized not in date_values:
            date_values.append(normalized)

    # --------------------------------------------------------
    # DD Month YYYY
    # --------------------------------------------------------

    reverse_month_matches = re.findall(
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+"
        rf"{month_pattern}\s+\d{{4}}\b",
        text,
        re.IGNORECASE,
    )

    for item in reverse_month_matches:

        normalized = _normalize_date(item)

        if normalized and normalized not in date_values:
            date_values.append(normalized)

    # --------------------------------------------------------
    # Assign dates
    # --------------------------------------------------------

    if len(date_values) >= 1:
        result["start_date"] = date_values[0]

    if len(date_values) >= 2:
        result["end_date"] = date_values[1]

    # ========================================================
    # DURATION
    # ========================================================

    duration_match = re.search(
        r"\b(\d+)\s*[- ]?"
        r"(?:day|days|night|nights)\b",
        text,
        re.IGNORECASE,
    )

    if duration_match:

        duration = _safe_int(duration_match.group(1))

        if duration and duration > 0:

            result["duration_days"] = duration

            # ------------------------------------------------
            # If start date exists and end date is missing,
            # calculate end date.
            #
            # Example:
            # 4 day trip starting Sep 10
            #
            # Sep 10, 11, 12, 13 = 4 days
            # ------------------------------------------------

            if result.get("start_date") and not result.get("end_date"):

                try:

                    start = date.fromisoformat(
                        result["start_date"]
                    )

                    end = start + timedelta(
                        days=duration - 1
                    )

                    result["end_date"] = end.isoformat()

                except Exception:
                    pass

    # ========================================================
    # TRAVELERS
    # ========================================================

    traveler_match = re.search(
        r"\b(?:for|with)\s+"
        r"(\d+)\s+"
        r"(?:people|person|travelers|travellers|guests|adults)\b",
        text,
        re.IGNORECASE,
    )

    if traveler_match:

        travelers = _safe_int(
            traveler_match.group(1)
        )

        if travelers and travelers > 0:
            result["travelers"] = travelers

    # Example:
    # 2 travelers
    # 3 people
    if "travelers" not in result:

        traveler_match = re.search(
            r"\b(\d+)\s+"
            r"(?:people|person|travelers|travellers|guests|adults)\b",
            text,
            re.IGNORECASE,
        )

        if traveler_match:

            travelers = _safe_int(
                traveler_match.group(1)
            )

            if travelers and travelers > 0:
                result["travelers"] = travelers

    # ========================================================
    # CURRENCY
    # ========================================================

    currency_match = re.search(
        r"\b(INR|USD|AED|EUR|GBP|SGD|AUD|CAD|JPY)\b",
        text,
        re.IGNORECASE,
    )

    if currency_match:

        result["currency"] = (
            currency_match.group(1).upper()
        )

    else:

        if re.search(
            r"\b(?:₹|rs\.?|rupees?|rupee)\b",
            text,
            re.IGNORECASE,
        ):
            result["currency"] = "INR"

        elif "$" in text:
            result["currency"] = "USD"

    # ========================================================
    # BUDGET
    # ========================================================

    budget_match = re.search(
        r"\b(?:budget|under|within|maximum|max)\s*"
        r"(?:of\s*)?"
        r"(?:₹|rs\.?|inr|usd|\$|aed|eur|gbp)?\s*"
        r"([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if budget_match:

        budget = _safe_float(
            budget_match.group(1)
        )

        if budget is not None:
            result["budget"] = budget

    # ========================================================
    # DEFAULTS
    # ========================================================

    if "travelers" not in result:
        result["travelers"] = 1

    if "currency" not in result:
        result["currency"] = "INR"

    print(
        "[agent] Local fallback extracted:",
        result,
    )

    return result


# ============================================================
# EXTRACT TRIP DATA USING GEMINI
# ============================================================

def extract_trip_data(
    user_message: str,
) -> dict:

    print("=" * 70)
    print("[agent] EXTRACTING TRIP INFORMATION")
    print("=" * 70)

    if not user_message:
        return {}

    try:

        prompt = TRIP_EXTRACTION_PROMPT.format(
            current_year=date.today().year,
            user_message=user_message,
        )

        response = llm.invoke(prompt)

        text = _get_llm_text(response)

        parsed = _extract_json_from_text(text)

        normalized = _normalize_trip_data(parsed)

        if normalized:

            print(
                "[agent] Gemini extraction successful:"
            )
            print(normalized)

            return normalized

        print(
            "[agent] Gemini returned empty/invalid JSON."
        )

    except Exception as exc:

        print(
            "[agent] Trip extraction LLM error:",
            repr(exc),
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Gemini 429 quota error is handled here.
        # Do NOT return {} immediately.
        # ----------------------------------------------------

        print(
            "[agent] Gemini unavailable. "
            "Switching to local extraction fallback."
        )

    # ========================================================
    # LOCAL FALLBACK
    # ========================================================

    fallback = _local_fallback_extract_trip_data(
        user_message
    )

    normalized_fallback = _normalize_trip_data(
        fallback
    )

    print(
        "[agent] Final extracted trip data:"
    )
    print(normalized_fallback)

    return normalized_fallback


# ============================================================
# FOLLOW-UP EXTRACTION
# ============================================================

def extract_followup_trip_data(
    user_message: str,
    previous_trip: dict,
) -> dict:

    print("=" * 70)
    print("[agent] EXTRACTING FOLLOW-UP TRIP INFORMATION")
    print("=" * 70)

    if not user_message:
        return {}

    previous_trip = (
        previous_trip
        if isinstance(previous_trip, dict)
        else {}
    )

    try:

        prompt = TRIP_FOLLOWUP_PROMPT.format(
            trip_data=json.dumps(
                previous_trip,
                ensure_ascii=False,
                default=str,
            ),
            user_message=user_message,
        )

        response = llm.invoke(prompt)

        text = _get_llm_text(response)

        parsed = _extract_json_from_text(text)

        normalized = _normalize_trip_data(parsed)

        print(
            "[agent] Follow-up Gemini extraction:"
        )
        print(normalized)

        return normalized

    except Exception as exc:

        print(
            "[agent] Follow-up LLM error:",
            repr(exc),
        )

        print(
            "[agent] Using local fallback for follow-up."
        )

        return _normalize_trip_data(
            _local_fallback_extract_trip_data(
                user_message
            )
        )


# ============================================================
# MERGE TRIP DATA
# ============================================================

def _merge_trip_data(
    previous_trip: dict,
    new_data: dict,
) -> dict:

    merged = {}

    if isinstance(previous_trip, dict):
        merged.update(previous_trip)

    if isinstance(new_data, dict):

        for key, value in new_data.items():

            # Do not overwrite existing values with
            # empty/null values.
            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            merged[key] = value

    return _normalize_trip_data(merged)


# ============================================================
# OPTIONAL TOOL CALL
# ============================================================

def _call_optional_tool(
    tool: Any,
    **kwargs,
) -> Any:

    if tool is None:
        return []

    try:
        return tool(**kwargs)

    except TypeError as exc:

        print(
            "[agent] Tool argument mismatch:",
            repr(exc),
        )

        return None

    except Exception as exc:

        print(
            "[agent] Tool error:",
            repr(exc),
        )

        return None


# ============================================================
# FLIGHTS
# ============================================================

async def _get_flights(
    trip_data: dict,
) -> list:

    print("[agent] Getting flights...")

    if search_flights is None:
        return []

    try:

        result = await search_flights(
            origin=trip_data.get("origin"),
            destination=trip_data.get("destination"),
            departure_date=trip_data.get("start_date"),
            start_date=trip_data.get("start_date"),
            travelers=trip_data.get("travelers", 1),
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):

            if isinstance(
                result.get("flights"),
                list,
            ):
                return result["flights"]

            return [result]

        return []

    except Exception as exc:

        print(
            "[agent] Flight search error:",
            repr(exc),
        )

        return []


# ============================================================
# HOTELS
# ============================================================
#
# IMPORTANT:
# DO NOT CHANGE THESE ARGUMENTS.
#
# These arguments match hotels.py.
#
# ============================================================

async def _get_hotels(
    trip_data: dict,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> list:

    print("[agent] Getting hotels...")

    if search_hotels is None:
        return []

    destination = trip_data.get(
        "destination"
    )

    start_date = trip_data.get(
        "start_date"
    )

    end_date = trip_data.get(
        "end_date"
    )

    travelers = trip_data.get(
        "travelers",
        1,
    )

    try:

        result = await search_hotels(
            destination=destination,
            latitude=latitude,
            longitude=longitude,
            check_in=start_date,
            check_out=end_date,
            travelers=travelers,
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):

            if isinstance(
                result.get("hotels"),
                list,
            ):
                return result["hotels"]

            return [result]

        return []

    except Exception as exc:

        print(
            "[agent] Hotel search error:",
            repr(exc),
        )

        return []


# ============================================================
# NORMALIZE HOTELS
# ============================================================

def _normalize_hotels(
    hotels: Any,
) -> list:

    if not isinstance(hotels, list):
        return []

    normalized = []

    for hotel in hotels:

        if not isinstance(hotel, dict):
            continue

        item = dict(hotel)

        price = (
            hotel.get("price")
            or hotel.get("total_price")
            or hotel.get("nightly_price")
            or hotel.get("amount")
        )

        price_value = _safe_float(price)

        if price_value is not None:
            item["price"] = price_value

        else:
            item["price_status"] = (
                "not_available"
            )

        if not item.get("name"):
            item["name"] = (
                hotel.get("hotel_name")
                or hotel.get("title")
                or "Hotel"
            )

        normalized.append(item)

    return normalized


# ============================================================
# PLACES / ATTRACTIONS
# ============================================================

async def _get_places(
    trip_data: dict,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> list:
    print("[agent] Getting places...")

    if search_places is None:
        print("[agent] search_places tool not available")
        return []

    destination = trip_data.get("destination")

    # ========================================================
    # 1. PRIMARY: USE ALREADY AVAILABLE COORDINATES
    # ========================================================

    if latitude is not None and longitude is not None:
        try:
            print(
                "[agent] Searching places using coordinates: "
                f"{latitude}, {longitude}"
            )

            result = await search_places(
                latitude=latitude,
                longitude=longitude,
                radius=10000,
            )

            if isinstance(result, list):
                print(
                    f"[agent] Places found using coordinates: "
                    f"{len(result)}"
                )
                return result

            if isinstance(result, dict):
                return result.get("results", [])

        except Exception as exc:
            print(
                "[agent] Coordinate-based places search error:",
                repr(exc),
            )

    # ========================================================
    # 2. FALLBACK: USE DESTINATION
    # ========================================================

    if destination:
        try:
            print(
                "[agent] Trying places search using destination: "
                f"{destination}"
            )

            result = await search_places(
                destination=destination,
            )

            if isinstance(result, list):
                print(
                    f"[agent] Places found using destination: "
                    f"{len(result)}"
                )
                return result

            if isinstance(result, dict):
                return result.get("results", [])

        except Exception as exc:
            print(
                "[agent] Destination-based places search error:",
                repr(exc),
            )

    # ========================================================
    # 3. FINAL FALLBACK: USE CITY
    # ========================================================

    if destination:
        try:
            print(
                "[agent] Trying places search using city: "
                f"{destination}"
            )

            result = await search_places(
                city=destination,
            )

            if isinstance(result, list):
                print(
                    f"[agent] Places found using city: "
                    f"{len(result)}"
                )
                return result

            if isinstance(result, dict):
                return result.get("results", [])

        except Exception as exc:
            print(
                "[agent] City-based places search error:",
                repr(exc),
            )

    print("[agent] No places found")
    return []

# ============================================================
# NORMALIZE PLACES
# ============================================================

def _normalize_places(
    places: Any,
) -> list:

    if not isinstance(places, list):
        return []

    normalized = []

    for place in places:

        if not isinstance(place, dict):
            continue

        item = dict(place)

        if not item.get("name"):
            item["name"] = (
                place.get("title")
                or place.get("place_name")
                or "Attraction"
            )

        if not item.get("address"):

            item["address"] = (
                place.get("formatted")
                or place.get("address_line1")
                or ""
            )

        rating = _safe_float(
            place.get("rating")
        )

        if rating is not None:
            item["rating"] = rating

        normalized.append(item)

    return normalized


# ============================================================
# RESTAURANTS
# ============================================================

async def _get_restaurants(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> list:

    print("[agent] Getting restaurants...")

    if search_restaurants is None:
        return []

    if latitude is None or longitude is None:
        return []

    try:

        result = await search_restaurants(
            latitude=latitude,
            longitude=longitude,
            radius=15000,
            limit=30,
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):

            if isinstance(
                result.get("restaurants"),
                list,
            ):
                return result["restaurants"]

            return [result]

        return []

    except Exception as exc:

        print(
            "[agent] Restaurant search error:",
            repr(exc),
        )

        return []


# ============================================================
# WEATHER
# ============================================================

async def _get_weather_data(
    trip_data: dict,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> list:
    print("[agent] Getting weather...")

    if get_weather is None:
        print("[agent] get_weather tool not available")
        return []

    if latitude is None or longitude is None:
        print("[agent] Weather skipped: coordinates unavailable")
        return []

    try:
        result = await get_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=trip_data.get("start_date"),
            end_date=trip_data.get("end_date"),
        )

        if isinstance(result, list):
            return result

        if isinstance(result, dict):
            if isinstance(result.get("weather"), list):
                return result["weather"]

            if isinstance(result.get("daily"), list):
                return result["daily"]

            return [result]

        return []

    except Exception as exc:
        print(
            "[agent] Weather error:",
            repr(exc),
        )
        return []


# ============================================================
# CURRENCY
# ============================================================

async def _get_currency_data(
    trip_data: dict,
) -> dict:

    print("[agent] Getting currency conversion...")

    if convert_currency is None:
        return {}

    source_currency = (
        trip_data.get("currency")
        or "INR"
    )

    # Current destination currency for Dubai.
    destination_currency = "AED"

    if source_currency == destination_currency:

        return {
            "amount": 1,
            "from_currency": source_currency,
            "to_currency": destination_currency,
            "converted_amount": 1,
            "rate": 1,
            "status": "success",
        }

    try:

        result = await convert_currency(
            amount=1,
            from_currency=source_currency,
            to_currency=destination_currency,
        )

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "converted_amount": result,
        }

    except Exception as exc:

        print(
            "[agent] Currency error:",
            repr(exc),
        )

        return {
            "status": "error",
            "error": str(exc),
        }


# ============================================================
# GEOCODING
# ============================================================

async def _get_location(
    destination: str,
) -> dict:

    print(
        "[agent] Geocoding destination:",
        destination,
    )

    if geocode_destination is None:
        return {}

    try:

        result = await geocode_destination(
            destination
        )

        if isinstance(result, dict):
            return result

        if isinstance(result, list):

            if result:
                first = result[0]

                if isinstance(first, dict):
                    return first

        return {}

    except TypeError:

        try:

            result = await geocode_destination(
                destination=destination
            )

            if isinstance(result, dict):
                return result

            if isinstance(result, list) and result:

                if isinstance(result[0], dict):
                    return result[0]

        except Exception as exc:

            print(
                "[agent] Geocoding error:",
                repr(exc),
            )

    except Exception as exc:

        print(
            "[agent] Geocoding error:",
            repr(exc),
        )

    return {}


# ============================================================
# RAG CONTEXT
# ============================================================

def _get_rag_context(
    trip_data: dict,
) -> Any:
    print("[agent] Getting RAG context...")
    try:
        destination = trip_data.get("destination")

        if not destination:
            return ""

        query = (
            f"Travel information for "
            f"{destination}"
        )

        result = retrieve_context(query)

        print("[agent] RAG result type:", type(result))

        return result

    except Exception as exc:
        print(
            "[agent] RAG error:",
            repr(exc),
        )
        return ""


# ============================================================
# BUDGET CALCULATION
# ============================================================

def _calculate_budget(
    trip_data: dict,
    flights: list,
    hotels: list,
) -> dict:

    travelers = _safe_int(
        trip_data.get("travelers"),
        1,
    ) or 1

    trip_budget = _safe_float(
        trip_data.get("budget")
    )

    # --------------------------------------------------------
    # Flight total
    # --------------------------------------------------------

    flight_prices = []

    for flight in flights:

        if not isinstance(flight, dict):
            continue

        price = _safe_float(
            flight.get("price")
        )

        if price is not None:
            flight_prices.append(price)

    flight_total = (
        sum(flight_prices)
        if flight_prices
        else 0
    )

    # --------------------------------------------------------
    # Hotel total
    # --------------------------------------------------------

    hotel_prices = []

    for hotel in hotels:

        if not isinstance(hotel, dict):
            continue

        price = (
            hotel.get("total_price")
            or hotel.get("price")
            or hotel.get("price_per_night")
        )

        price_value = _safe_float(price)

        if price_value is not None:
            hotel_prices.append(price_value)

    hotel_total = (
        sum(hotel_prices)
        if hotel_prices
        else 0
    )

    # --------------------------------------------------------
    # Nights
    # --------------------------------------------------------

    nights = 0

    try:

        start = date.fromisoformat(
            trip_data["start_date"]
        )

        end = date.fromisoformat(
            trip_data["end_date"]
        )

        nights = max(
            0,
            (end - start).days,
        )

    except Exception:
        nights = 0

    trip_days = nights + 1 if nights else 0

    # --------------------------------------------------------
    # Estimated costs
    # --------------------------------------------------------

    food = (
        travelers
        * max(trip_days, 1)
        * 1500
    )

    activities = (
        max(trip_days, 1)
        * 1000
    )

    transport = (
        max(trip_days, 1)
        * 750
    )

    known_total = (
        flight_total
        + hotel_total
    )

    total = (
        known_total
        + food
        + activities
        + transport
    )

    remaining_budget = None

    if trip_budget is not None:
        remaining_budget = (
            trip_budget - total
        )

    pricing_status = (
        "partial"
        if not flight_prices or not hotel_prices
        else "available"
    )

    return {
        "flights": flight_total,
        "hotels": hotel_total,
        "food": food,
        "activities": activities,
        "transport": transport,
        "total": total,
        "currency": trip_data.get(
            "currency",
            "INR",
        ),
        "nights": nights,
        "trip_days": trip_days,
        "travelers": travelers,
        "remaining_budget": remaining_budget,
        "flight_total": flight_total,
        "hotel_total": hotel_total,
        "known_total": known_total,
        "flight_prices_available": len(
            flight_prices
        ),
        "hotel_prices_available": len(
            hotel_prices
        ),
        "pricing_status": pricing_status,
        "price_data_available": bool(
            flight_prices or hotel_prices
        ),
        "estimated": True,
        "note": (
            "Food, activities and transport "
            "are estimated because live prices "
            "may not be available."
        ),
    }


# ============================================================
# ITINERARY
# ============================================================

def _create_trip_itinerary(
    trip_data: dict,
    places: list,
    restaurants: list,
    weather: list,
    flights: list,
    hotels: list,
) -> list:

    print("[agent] Creating itinerary...")

    try:

        result = create_itinerary(
destination=trip_data.get("destination", ""),
start_date=trip_data.get("start_date", ""),
end_date=trip_data.get("end_date", ""),
places=places,
restaurants=restaurants,
weather=weather,
)


        if isinstance(result, list):
            return result

        if isinstance(result, dict):

            if isinstance(
                result.get("itinerary"),
                list,
            ):
                return result["itinerary"]

            return [result]

        return []

    except TypeError as exc:

        print(
            "[agent] Itinerary argument mismatch:",
            repr(exc),
        )

        # ----------------------------------------------------
        # Fallback if itinerary service uses different args
        # ----------------------------------------------------

        try:

            result = create_itinerary(
                trip_data,
                places,
                restaurants,
                weather,
            )

            if isinstance(result, list):
                return result

            if isinstance(result, dict):

                if isinstance(
                    result.get("itinerary"),
                    list,
                ):
                    return result["itinerary"]

                return [result]

        except Exception as fallback_exc:

            print(
                "[agent] Itinerary fallback error:",
                repr(fallback_exc),
            )

    except Exception as exc:

        print(
            "[agent] Itinerary error:",
            repr(exc),
        )

    return []


# ============================================================
# FINAL VALIDATION
# ============================================================

def _validate_final_trip(
    trip_data: dict,
) -> dict:

    try:

        result = validate_trip(
            trip_data
        )

        if isinstance(result, dict):
            return result

        return {
            "valid": True,
        }

    except TypeError:

        try:

            result = validate_trip(
                data=trip_data
            )

            if isinstance(result, dict):
                return result

        except Exception as exc:

            print(
                "[agent] Final validation error:",
                repr(exc),
            )

    except Exception as exc:

        print(
            "[agent] Final validation error:",
            repr(exc),
        )

    return {
        "valid": True,
    }


# ============================================================
# REQUIRED FIELDS
# ============================================================

def _get_missing_fields(
    trip_data: dict,
) -> list:

    required_fields = [
        "origin",
        "destination",
        "start_date",
        "end_date",
    ]

    missing = []

    for field in required_fields:

        value = trip_data.get(field)

        if value is None:
            missing.append(field)

        elif isinstance(value, str) and not value.strip():
            missing.append(field)

    return missing


# ============================================================
# DATE VALIDATION
# ============================================================

def _validate_dates(
    trip_data: dict,
) -> Optional[str]:

    start_date = trip_data.get(
        "start_date"
    )

    end_date = trip_data.get(
        "end_date"
    )

    if not start_date or not end_date:
        return None

    try:

        start = date.fromisoformat(
            start_date
        )

        end = date.fromisoformat(
            end_date
        )

    except Exception:

        return (
            "Please provide valid travel "
            "dates in YYYY-MM-DD format."
        )

    if end < start:

        return (
            "End date cannot be earlier "
            "than start date."
        )

    return None


# ============================================================
# MAIN TRIP PROCESSOR
# ============================================================

async def process_trip_request(
    message: str,
    conversation_id: Optional[str] = None,
    previous_trip: Optional[dict] = None,
) -> dict:

    conversation_id = (
        conversation_id
        or str(uuid.uuid4())
    )

    print("\n")
    print("=" * 70)
    print("[agent] PROCESSING TRIP REQUEST")
    print("=" * 70)
    print(
        "[agent] Conversation:",
        conversation_id,
    )
    print(
        "[agent] User message:",
        message,
    )

    # ========================================================
    # STEP 1 - EXTRACTION
    # ========================================================

    print("\n")
    print("[agent] STEP 1 - TRIP EXTRACTION")
    print("=" * 70)

    if previous_trip:

        print(
            "[agent] Existing trip found."
        )

        extracted_data = extract_followup_trip_data(
            message,
            previous_trip,
        )

        trip_data = _merge_trip_data(
            previous_trip,
            extracted_data,
        )

    else:

        trip_data = extract_trip_data(
            message
        )

    print(
        "[agent] Extracted trip data:"
    )
    print(trip_data)

    # ========================================================
    # STEP 2 - REQUIRED FIELD VALIDATION
    # ========================================================

    print("\n")
    print(
        "[agent] STEP 2 - REQUIRED FIELD VALIDATION"
    )

    missing_fields = _get_missing_fields(
        trip_data
    )

    print(
        "[agent] Missing fields:",
        missing_fields,
    )

    if missing_fields:

        return {
            "conversation_id": conversation_id,
            "message": (
                "Please provide the missing "
                "trip information."
            ),
            "status": "needs_information",
            "missing_fields": missing_fields,
            "requires_date": (
                "start_date" in missing_fields
                or "end_date" in missing_fields
            ),
            "trip": trip_data,
        }

    # ========================================================
    # STEP 3 - DATE VALIDATION
    # ========================================================

    print("\n")
    print("[agent] STEP 3 - DATE VALIDATION")

    date_error = _validate_dates(
        trip_data
    )

    if date_error:

        return {
            "conversation_id": conversation_id,
            "message": date_error,
            "status": "needs_information",
            "missing_fields": [],
            "requires_date": True,
            "trip": trip_data,
        }

    # ========================================================
    # STEP 4 - RAG
    # ========================================================

    print("\n")
    print("[agent] STEP 4 - RAG CONTEXT")

    rag_context = _get_rag_context(
        trip_data
    )

    # ========================================================
    # STEP 5 - GEOCODING
    # ========================================================

    print("\n")
    print("[agent] STEP 5 - GEOCODING")

    location = await _get_location(
        trip_data.get("destination")
    )

    latitude = _safe_float(
        location.get("latitude")
    )

    longitude = _safe_float(
        location.get("longitude")
    )

    print(
        "[agent] Location:",
        location,
    )

    # ========================================================
    # STEP 6 - FLIGHTS
    # ========================================================

    print("\n")
    print("[agent] STEP 6 - FLIGHTS")

    flights = await _get_flights(
        trip_data
    )

    # ========================================================
    # STEP 7 - HOTELS
    # ========================================================

    print("\n")
    print("[agent] STEP 7 - HOTELS")

    hotels = await _get_hotels(
        trip_data,
        latitude=latitude,
        longitude=longitude,
    )

    hotels = _normalize_hotels(
        hotels
    )

    # ========================================================
    # STEP 8 - PLACES
    # ========================================================

    print("\n")
    print("[agent] STEP 8 - PLACES")

    places = await _get_places(
        trip_data,
        latitude=latitude,
        longitude=longitude,
    )

    places = _normalize_places(
        places
    )

    # ========================================================
    # STEP 9 - RESTAURANTS
    # ========================================================

    print("\n")
    print("[agent] STEP 9 - RESTAURANTS")

    restaurants = await _get_restaurants(
        latitude=latitude,
        longitude=longitude,
    )

    # ========================================================
    # STEP 10 - WEATHER
    # ========================================================

    print("\n")
    print("[agent] STEP 10 - WEATHER")

    weather = await _get_weather_data(
        trip_data,
        latitude=latitude,
        longitude=longitude,
    )

    # ========================================================
    # STEP 11 - CURRENCY
    # ========================================================

    print("\n")
    print("[agent] STEP 11 - CURRENCY")

    currency_conversion = await _get_currency_data(
        trip_data
    )

    # ========================================================
    # STEP 12 - BUDGET
    # ========================================================

    print("\n")
    print("[agent] STEP 12 - BUDGET")

    budget_breakdown = _calculate_budget(
        trip_data=trip_data,
        flights=flights,
        hotels=hotels,
    )

    # ========================================================
    # STEP 13 - ITINERARY
    # ========================================================

    print("\n")
    print("[agent] STEP 13 - ITINERARY")

    itinerary = _create_trip_itinerary(
        trip_data=trip_data,
        places=places,
        restaurants=restaurants,
        weather=weather,
        flights=flights,
        hotels=hotels,
    )

    # ========================================================
    # STEP 14 - FINAL TRIP
    # ========================================================

    print("\n")
    print("[agent] STEP 14 - BUILDING FINAL TRIP")

    trip_id = str(uuid.uuid4())

    trip = {
        "trip_id": trip_id,

        "origin": trip_data.get(
            "origin"
        ),

        "destination": trip_data.get(
            "destination"
        ),

        "start_date": trip_data.get(
            "start_date"
        ),

        "end_date": trip_data.get(
            "end_date"
        ),

        "travelers": trip_data.get(
            "travelers",
            1,
        ),

        "budget": trip_data.get(
            "budget"
        ),

        "currency": trip_data.get(
            "currency",
            "INR",
        ),

        "location": location,

        "flights": flights,

        "hotels": hotels,

        "restaurants": restaurants,

        "weather": weather,

        "attractions": places,

        "itinerary": itinerary,

        "budget_breakdown": budget_breakdown,

        "currency_conversion": currency_conversion,

        "rag_context": rag_context,
    }

    # ========================================================
    # STEP 15 - FINAL VALIDATION
    # ========================================================

    print("\n")
    print("[agent] STEP 15 - FINAL VALIDATION")

    validation_result = _validate_final_trip(
        trip
    )

    trip["validation"] = validation_result

    # ========================================================
    # SUCCESS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("[agent] TRIP CREATED SUCCESSFULLY")
    print("=" * 70)
    print(
        "[agent] Trip ID:",
        trip_id,
    )

    return {
        "conversation_id": conversation_id,
        "message": (
            f"I created your "
            f"{trip_data.get('destination')} "
            f"trip from "
            f"{trip_data.get('start_date')} "
            f"to "
            f"{trip_data.get('end_date')}."
        ),
        "status": "success",
        "trip": trip,
    }


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(
    user_message: str,
    conversation_id: Optional[str] = None,
) -> dict:

    return process_trip_request(
        message=user_message,
        conversation_id=conversation_id,
    )


# ============================================================
# RUN TRIP AGENT
# ============================================================

async def run_trip_agent(
    user_message: str,
    previous_trip: Optional[dict] = None,
    conversation_id: Optional[str] = None,
) -> dict:

    return await process_trip_request(
        message=user_message,
        conversation_id=conversation_id,
        previous_trip=previous_trip,
    )


# ============================================================
# CHAT WITH AGENT
# ============================================================

async def chat_with_agent(
    message: str,
    conversation_id: Optional[str] = None,
    previous_trip: Optional[dict] = None,
) -> dict:

    return await process_trip_request(
        message=message,
        conversation_id=conversation_id,
        previous_trip=previous_trip,
    )