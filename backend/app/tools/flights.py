# app/tools/flights.py

from datetime import datetime
from typing import Any

import httpx

from app.config import settings


# ============================================================
# SERPAPI GOOGLE FLIGHTS CONFIGURATION
# ============================================================

SERPAPI_BASE_URL = getattr(
    settings,
    "serpapi_base_url",
    "https://serpapi.com/search.json",
).rstrip("/")


# ============================================================
# AIRPORT CODES
# ============================================================

AIRPORT_CODES: dict[str, str] = {
    # ========================================================
    # INDIA
    # ========================================================
    "chennai": "MAA",
    "madras": "MAA",

    "mumbai": "BOM",
    "bombay": "BOM",

    "delhi": "DEL",
    "new delhi": "DEL",

    "bangalore": "BLR",
    "bengaluru": "BLR",

    "hyderabad": "HYD",

    "kochi": "COK",
    "cochin": "COK",

    "coimbatore": "CJB",

    "madurai": "IXM",

    "goa": "GOI",

    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",

    "ahmedabad": "AMD",

    "pune": "PNQ",

    "kolkata": "CCU",
    "calcutta": "CCU",

    "jaipur": "JAI",

    "lucknow": "LKO",

    "varanasi": "VNS",

    "visakhapatnam": "VTZ",

    "bhubaneswar": "BBI",

    "tiruchirappalli": "TRZ",
    "trichy": "TRZ",

    # ========================================================
    # UAE
    # ========================================================
    "dubai": "DXB",

    "abu dhabi": "AUH",

    "sharjah": "SHJ",

    # ========================================================
    # ASIA
    # ========================================================
    "singapore": "SIN",

    "kuala lumpur": "KUL",

    "bangkok": "BKK",

    "phuket": "HKT",

    "bali": "DPS",
    "denpasar": "DPS",

    "jakarta": "CGK",

    "manila": "MNL",

    "hong kong": "HKG",

    "seoul": "ICN",

    # ========================================================
    # EUROPE
    # ========================================================
    "london": "LHR",

    "paris": "CDG",

    "frankfurt": "FRA",

    "amsterdam": "AMS",

    "rome": "FCO",

    "madrid": "MAD",

    "barcelona": "BCN",

    "zurich": "ZRH",

    "istanbul": "IST",

    # ========================================================
    # JAPAN
    # ========================================================
    "tokyo": "NRT",

    "tokyo haneda": "HND",

    "osaka": "KIX",

    # ========================================================
    # USA
    # ========================================================
    "new york": "JFK",

    "los angeles": "LAX",

    "san francisco": "SFO",

    "chicago": "ORD",

    "miami": "MIA",

    "boston": "BOS",

    "washington": "IAD",

    # ========================================================
    # AUSTRALIA
    # ========================================================
    "sydney": "SYD",

    "melbourne": "MEL",

    "perth": "PER",

    "brisbane": "BNE",
}


# ============================================================
# AIRPORT CODE RESOLVER
# ============================================================

def _airport_code(city: str | None) -> str | None:
    """
    Convert city name or IATA code to IATA airport code.
    """

    if not city:
        return None

    normalized = str(city).strip().lower()

    if not normalized:
        return None

    # Already an IATA code
    if len(normalized) == 3:
        return normalized.upper()

    return AIRPORT_CODES.get(normalized)


# ============================================================
# DATE VALIDATION
# ============================================================

def _normalize_date(value: str | None) -> str | None:
    """
    Normalize date to YYYY-MM-DD.
    """

    if not value:
        return None

    value = str(value).strip()

    if len(value) < 10:
        return None

    candidate = value[:10]

    try:
        datetime.strptime(
            candidate,
            "%Y-%m-%d",
        )

        return candidate

    except ValueError:
        return None


# ============================================================
# SAFE TRAVELERS
# ============================================================

def _safe_travelers(
    travelers: Any,
) -> int:
    """
    Safely convert travelers to integer.
    """

    try:
        return max(
            1,
            int(travelers or 1),
        )

    except (
        TypeError,
        ValueError,
    ):
        return 1


# ============================================================
# FORMAT DURATION
# ============================================================

def _format_duration(
    minutes: Any,
) -> str | None:
    """
    Convert minutes into human-readable duration.

    Example:
        240 -> 4h 0m
        95  -> 1h 35m
    """

    if minutes is None:
        return None

    try:
        total_minutes = int(minutes)

    except (
        TypeError,
        ValueError,
    ):
        return None

    if total_minutes < 0:
        return None

    hours = total_minutes // 60
    remaining_minutes = total_minutes % 60

    if hours > 0:
        return f"{hours}h {remaining_minutes}m"

    return f"{remaining_minutes}m"


# ============================================================
# GET AIRPORT INFORMATION
# ============================================================

def _get_airport_info(
    airport: Any,
) -> tuple[
    str | None,
    str | None,
    str | None,
]:
    """
    Extract airport:

    Returns:
        airport_name
        airport_code
        airport_time
    """

    if not isinstance(
        airport,
        dict,
    ):
        return (
            None,
            None,
            None,
        )

    name = airport.get("name")

    code = (
        airport.get("id")
        or airport.get("iata")
        or airport.get("iataCode")
        or airport.get("code")
    )

    time = (
        airport.get("time")
        or airport.get("datetime")
        or airport.get("date")
    )

    if code:
        code = str(code).upper()

    return (
        name,
        code,
        time,
    )


# ============================================================
# GET FLIGHT SEGMENTS
# ============================================================

def _get_segments(
    itinerary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Get individual flight segments from a SerpApi itinerary.
    """

    flights = itinerary.get("flights")

    if not isinstance(
        flights,
        list,
    ):
        return []

    return [
        item
        for item in flights
        if isinstance(
            item,
            dict,
        )
    ]


# ============================================================
# NORMALIZE SERPAPI FLIGHT
# ============================================================

def _normalize_flight(
    itinerary: dict[str, Any],
    travelers: int,
    origin_code: str,
    destination_code: str,
) -> dict[str, Any] | None:
    """
    Convert SerpApi Google Flights itinerary
    into the application's existing flight structure.
    """

    segments = _get_segments(
        itinerary
    )

    if not segments:
        return None

    # ========================================================
    # FIRST SEGMENT
    # ========================================================

    first_segment = segments[0]

    # ========================================================
    # LAST SEGMENT
    # ========================================================

    last_segment = segments[-1]

    # ========================================================
    # DEPARTURE
    # ========================================================

    departure_name = None
    departure_airport = origin_code
    departure_time = None

    (
        departure_name,
        parsed_departure_code,
        departure_time,
    ) = _get_airport_info(
        first_segment.get(
            "departure_airport"
        )
    )

    if parsed_departure_code:
        departure_airport = parsed_departure_code

    # ========================================================
    # ARRIVAL
    # ========================================================

    arrival_name = None
    arrival_airport = destination_code
    arrival_time = None

    (
        arrival_name,
        parsed_arrival_code,
        arrival_time,
    ) = _get_airport_info(
        last_segment.get(
            "arrival_airport"
        )
    )

    if parsed_arrival_code:
        arrival_airport = parsed_arrival_code

    # ========================================================
    # AIRLINE
    # ========================================================

    airlines: list[str] = []

    for segment in segments:
        airline = segment.get(
            "airline"
        )

        if airline:
            airline = str(airline)

            if airline not in airlines:
                airlines.append(
                    airline
                )

    airline_name = (
        ", ".join(airlines)
        if airlines
        else "Unknown Airline"
    )

    # ========================================================
    # FLIGHT NUMBERS
    # ========================================================

    flight_numbers: list[str] = []

    for segment in segments:
        flight_number = segment.get(
            "flight_number"
        )

        if flight_number:
            flight_number = str(
                flight_number
            )

            if flight_number not in flight_numbers:
                flight_numbers.append(
                    flight_number
                )

    flight_number_value = (
        ", ".join(flight_numbers)
        if flight_numbers
        else None
    )

    # ========================================================
    # DURATION
    # ========================================================

    total_duration = itinerary.get(
        "total_duration"
    )

    if total_duration is None:
        durations = []

        for segment in segments:
            duration = segment.get(
                "duration"
            )

            if duration is not None:
                try:
                    durations.append(
                        int(duration)
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

        if durations:
            total_duration = sum(
                durations
            )

    duration_text = _format_duration(
        total_duration
    )

    # ========================================================
    # PRICE
    # ========================================================

    price = itinerary.get(
        "price"
    )

    if price is not None:
        try:
            price = float(price)

            if price.is_integer():
                price = int(price)

        except (
            TypeError,
            ValueError,
        ):
            price = None

    # ========================================================
    # CURRENCY
    # ========================================================

    currency = "INR"

    # ========================================================
    # TRAVEL CLASS
    # ========================================================

    travel_class = None

    for segment in segments:
        value = segment.get(
            "travel_class"
        )

        if value:
            travel_class = str(
                value
            )
            break

    # ========================================================
    # AIRCRAFT
    # ========================================================

    aircraft = None

    aircraft_values: list[str] = []

    for segment in segments:
        airplane = segment.get(
            "airplane"
        )

        if airplane:
            airplane = str(
                airplane
            )

            if airplane not in aircraft_values:
                aircraft_values.append(
                    airplane
                )

    if aircraft_values:
        aircraft = ", ".join(
            aircraft_values
        )

    # ========================================================
    # AIRLINE LOGO
    # ========================================================

    airline_logo = None

    for segment in segments:
        logo = segment.get(
            "airline_logo"
        )

        if logo:
            airline_logo = str(
                logo
            )
            break

    # ========================================================
    # STOPS
    # ========================================================

    stops = max(
        0,
        len(segments) - 1,
    )

    if stops == 0:
        stops_text = "Nonstop"
    elif stops == 1:
        stops_text = "1 stop"
    else:
        stops_text = f"{stops} stops"

    # ========================================================
    # BOOKING TOKEN
    # ========================================================

    booking_token = itinerary.get(
        "booking_token"
    )

    # ========================================================
    # DEPARTURE TOKEN
    # ========================================================

    departure_token = itinerary.get(
        "departure_token"
    )

    # ========================================================
    # PRICE STATUS
    # ========================================================

    if price is not None:
        price_status = "available"
    else:
        price_status = "not_available"

    # ========================================================
    # FINAL NORMALIZED OBJECT
    # ========================================================

    return {
        # Existing application fields
        "flight_number": flight_number_value,

        "airline": airline_name,

        "airline_code": None,

        "departure_airport": (
            departure_airport
        ),

        "arrival_airport": (
            arrival_airport
        ),

        "departure_time": (
            departure_time
        ),

        "arrival_time": (
            arrival_time
        ),

        "status": "scheduled",

        "price": price,

        "currency": currency,

        "travelers": travelers,

        "source": "serpapi_google_flights",

        "price_status": price_status,

        # Additional useful fields
        "departure_airport_name": (
            departure_name
        ),

        "arrival_airport_name": (
            arrival_name
        ),

        "duration": (
            total_duration
        ),

        "duration_text": (
            duration_text
        ),

        "stops": stops,

        "stops_text": stops_text,

        "travel_class": (
            travel_class
        ),

        "aircraft": aircraft,

        "airline_logo": airline_logo,

        "booking_token": (
            booking_token
        ),

        "departure_token": (
            departure_token
        ),
    }


# ============================================================
# SEARCH FLIGHTS
# ============================================================

async def search_flights(
    origin: str,
    destination: str,
    start_date: str | None = None,
    travelers: int = 1,
    departure_date: str | None = None,
    return_date: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search Google Flights through SerpApi.

    Compatible with the existing application interface.

    Example:

        await search_flights(
            origin="Chennai",
            destination="Dubai",
            start_date="2026-09-16",
            travelers=1,
        )
    """

    # ========================================================
    # SERPAPI API KEY
    # ========================================================

    api_key = getattr(
        settings,
        "serpapi_api_key",
        None,
    )

    if not api_key:
        print(
            "[serpapi] ERROR: "
            "SERPAPI_API_KEY is missing."
        )
        return []

    api_key = str(
        api_key
    ).strip()

    if not api_key:
        print(
            "[serpapi] ERROR: "
            "SERPAPI_API_KEY is empty."
        )
        return []

    # ========================================================
    # DATE
    # ========================================================

    requested_date = (
        _normalize_date(
            start_date
        )
        or _normalize_date(
            departure_date
        )
    )

    if not requested_date:
        print(
            "[serpapi] ERROR: "
            "Valid departure date is required."
        )
        return []

    # ========================================================
    # TRAVELERS
    # ========================================================

    travelers_value = _safe_travelers(
        travelers
    )

    # ========================================================
    # AIRPORTS
    # ========================================================

    origin_code = _airport_code(
        origin
    )

    destination_code = _airport_code(
        destination
    )

    if not origin_code:
        print(
            "[serpapi] ERROR: "
            f"Unknown origin airport: {origin}"
        )
        return []

    if not destination_code:
        print(
            "[serpapi] ERROR: "
            f"Unknown destination airport: "
            f"{destination}"
        )
        return []

    # ========================================================
    # SAME AIRPORT
    # ========================================================

    if origin_code == destination_code:
        print(
            "[serpapi] ERROR: "
            "Origin and destination are identical."
        )
        return []

    # ========================================================
    # RETURN DATE
    # ========================================================

    requested_return_date = _normalize_date(
        return_date
    )

    # ========================================================
    # FLIGHT TYPE
    # ========================================================

    if requested_return_date:
        flight_type = "1"
    else:
        flight_type = "2"

    # ========================================================
    # SERPAPI PARAMETERS
    # ========================================================

    params: dict[str, Any] = {
        "engine": "google_flights",

        "api_key": api_key,

        "departure_id": origin_code,

        "arrival_id": destination_code,

        "type": flight_type,

        "outbound_date": requested_date,

        "currency": "INR",

        "hl": "en",

        "gl": "in",

        "adults": travelers_value,

        # Keep false for normal/faster POC searches.
        "deep_search": "false",
    }

    if requested_return_date:
        params["return_date"] = (
            requested_return_date
        )

    # ========================================================
    # DEBUG
    # ========================================================

    print("=" * 70)

    print(
        "[serpapi] GOOGLE FLIGHTS SEARCH"
    )

    print(
        "[serpapi] Origin:",
        origin,
        "=>",
        origin_code,
    )

    print(
        "[serpapi] Destination:",
        destination,
        "=>",
        destination_code,
    )

    print(
        "[serpapi] Departure date:",
        requested_date,
    )

    print(
        "[serpapi] Return date:",
        requested_return_date,
    )

    print(
        "[serpapi] Travelers:",
        travelers_value,
    )

    print(
        "[serpapi] Currency:",
        "INR",
    )

    print(
        "[serpapi] Base URL:",
        SERPAPI_BASE_URL,
    )

    print(
        "[serpapi] API key configured:",
        bool(api_key),
    )

    print("=" * 70)

    # ========================================================
    # HTTP REQUEST
    # ========================================================

    try:
        timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                SERPAPI_BASE_URL,
                params=params,
            )

        print(
            "[serpapi] HTTP status:",
            response.status_code,
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if response.status_code == 200:

            print(
                "[serpapi] API request successful."
            )

        # ====================================================
        # BAD REQUEST
        # ====================================================

        elif response.status_code == 400:

            print(
                "[serpapi] ERROR 400: "
                "Invalid request."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # UNAUTHORIZED
        # ====================================================

        elif response.status_code == 401:

            print(
                "[serpapi] ERROR 401: "
                "Invalid or missing API key."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # FORBIDDEN
        # ====================================================

        elif response.status_code == 403:

            print(
                "[serpapi] ERROR 403: "
                "Request is forbidden."
            )

            print(
                "[serpapi] Check your SerpApi "
                "subscription/quota."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # NOT FOUND
        # ====================================================

        elif response.status_code == 404:

            print(
                "[serpapi] ERROR 404: "
                "SerpApi endpoint not found."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # RATE LIMIT
        # ====================================================

        elif response.status_code == 429:

            print(
                "[serpapi] ERROR 429: "
                "Rate limit exceeded."
            )

            print(
                "[serpapi] Check your SerpApi quota."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # SERVER ERROR
        # ====================================================

        elif response.status_code >= 500:

            print(
                "[serpapi] ERROR:",
                response.status_code,
            )

            print(
                "[serpapi] SerpApi server error."
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # OTHER ERROR
        # ====================================================

        else:

            print(
                "[serpapi] ERROR:",
                response.status_code,
            )

            print(
                "[serpapi] Response:",
                response.text[:3000],
            )

            return []

    # ========================================================
    # TIMEOUT
    # ========================================================

    except httpx.TimeoutException:

        print(
            "[serpapi] ERROR: "
            "SerpApi request timed out."
        )

        return []

    # ========================================================
    # HTTP ERROR
    # ========================================================

    except httpx.HTTPError as error:

        print(
            "[serpapi] HTTP error:",
            repr(error),
        )

        return []

    # ========================================================
    # UNKNOWN ERROR
    # ========================================================

    except Exception as error:

        print(
            "[serpapi] Unexpected error:",
            repr(error),
        )

        return []

    # ========================================================
    # JSON RESPONSE
    # ========================================================

    try:

        data = response.json()

    except ValueError:

        print(
            "[serpapi] ERROR: "
            "Response is not valid JSON."
        )

        print(
            "[serpapi] Response:",
            response.text[:3000],
        )

        return []

    # ========================================================
    # RESPONSE TYPE
    # ========================================================

    if not isinstance(
        data,
        dict,
    ):

        print(
            "[serpapi] ERROR: "
            "Unexpected response format."
        )

        return []

    # ========================================================
    # RESPONSE DEBUG
    # ========================================================

    print(
        "[serpapi] Response keys:",
        list(
            data.keys()
        ),
    )

    # ========================================================
    # API ERROR
    # ========================================================

    if data.get("error"):

        print(
            "[serpapi] API error:",
            data.get("error"),
        )

        return []

    # ========================================================
    # GET BEST FLIGHTS
    # ========================================================

    best_flights = data.get(
        "best_flights",
        [],
    )

    if not isinstance(
        best_flights,
        list,
    ):
        best_flights = []

    # ========================================================
    # GET OTHER FLIGHTS
    # ========================================================

    other_flights = data.get(
        "other_flights",
        [],
    )

    if not isinstance(
        other_flights,
        list,
    ):
        other_flights = []

    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    raw_flights: list[
        dict[str, Any]
    ] = []

    for item in best_flights:

        if isinstance(
            item,
            dict,
        ):
            raw_flights.append(
                item
            )

    for item in other_flights:

        if isinstance(
            item,
            dict,
        ):
            raw_flights.append(
                item
            )

    print(
        "[serpapi] Best flights:",
        len(best_flights),
    )

    print(
        "[serpapi] Other flights:",
        len(other_flights),
    )

    print(
        "[serpapi] Total itineraries:",
        len(raw_flights),
    )

    # ========================================================
    # NORMALIZE
    # ========================================================

    results: list[
        dict[str, Any]
    ] = []

    seen: set[str] = set()

    for itinerary in raw_flights:

        normalized = _normalize_flight(
            itinerary=itinerary,
            travelers=travelers_value,
            origin_code=origin_code,
            destination_code=destination_code,
        )

        if not normalized:
            continue

        # ----------------------------------------------------
        # Ignore invalid records
        # ----------------------------------------------------

        if not normalized.get(
            "flight_number"
        ):

            continue

        # ----------------------------------------------------
        # Duplicate key
        # ----------------------------------------------------

        key = (
            f"{normalized.get('flight_number')}-"
            f"{normalized.get('departure_airport')}-"
            f"{normalized.get('arrival_airport')}-"
            f"{normalized.get('departure_time')}-"
            f"{normalized.get('price')}"
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            normalized
        )

    # ========================================================
    # PRICE INSIGHTS
    # ========================================================

    price_insights = data.get(
        "price_insights"
    )

    if isinstance(
        price_insights,
        dict,
    ):

        lowest_price = price_insights.get(
            "lowest_price"
        )

        print(
            "[serpapi] Lowest price:",
            lowest_price,
        )

        print(
            "[serpapi] Price level:",
            price_insights.get(
                "price_level"
            ),
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "[serpapi] Final flight count:",
        len(results),
    )

    if results:

        print(
            "[serpapi] First flight:",
            results[0],
        )

    else:

        print(
            "[serpapi] No flights returned."
        )

    print("=" * 70)

    return results[:20]