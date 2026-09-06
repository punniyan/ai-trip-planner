# app/tools/flights.py

from datetime import datetime
from typing import Any

import httpx

from app.config import settings


# ============================================================
# CIRIUM CONFIGURATION
# ============================================================

CIRIUM_BASE_URL = getattr(
    settings,
    "cirium_base_url",
    "https://api.sky.cirium.com/v1",
).rstrip("/")


# ============================================================
# AIRPORT CODES
# ============================================================

AIRPORT_CODES: dict[str, str] = {
    # INDIA
    "chennai": "MAA",
    "mumbai": "BOM",
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

    # UAE
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",

    # ASIA
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "bangkok": "BKK",
    "phuket": "HKT",
    "bali": "DPS",

    # EUROPE
    "london": "LHR",
    "paris": "CDG",
    "frankfurt": "FRA",
    "amsterdam": "AMS",
    "rome": "FCO",
    "madrid": "MAD",

    # JAPAN
    "tokyo": "NRT",
    "osaka": "KIX",

    # USA
    "new york": "JFK",
    "los angeles": "LAX",
    "san francisco": "SFO",
    "chicago": "ORD",
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
# AIRPORT OBJECT PARSER
# ============================================================

def _get_airport_code_from_object(
    airport: Any,
) -> str | None:

    if isinstance(airport, str):
        return airport.upper()

    if not isinstance(
        airport,
        dict,
    ):
        return None

    code = (
        airport.get("iata")
        or airport.get("iataCode")
        or airport.get("fsCode")
        or airport.get("requestedCode")
        or airport.get("code")
    )

    if code:
        return str(code).upper()

    return None


# ============================================================
# TIME OBJECT PARSER
# ============================================================

def _get_time_from_object(
    value: Any,
) -> str | None:

    if isinstance(value, str):
        return value

    if not isinstance(
        value,
        dict,
    ):
        return None

    return (
        value.get("date")
        or value.get("time")
        or value.get("scheduled")
        or value.get("scheduledTime")
        or value.get("estimated")
        or value.get("actual")
    )


# ============================================================
# AIRLINE PARSER
# ============================================================

def _get_airline(
    flight: dict[str, Any],
) -> tuple[str | None, str | None]:

    carrier = (
        flight.get("carrier")
        or flight.get("airline")
        or {}
    )

    # Example:
    # "carrier": "EK"
    if isinstance(
        carrier,
        str,
    ):
        return carrier, None

    if not isinstance(
        carrier,
        dict,
    ):
        return None, None

    airline_name = (
        carrier.get("name")
        or carrier.get("nameOfficial")
        or carrier.get("nameShort")
    )

    airline_code = (
        carrier.get("iata")
        or carrier.get("fsCode")
        or carrier.get("icao")
        or carrier.get("requestedCode")
    )

    if airline_code:
        airline_code = str(
            airline_code
        ).upper()

    return (
        airline_name,
        airline_code,
    )


# ============================================================
# FLIGHT NUMBER PARSER
# ============================================================

def _get_flight_number(
    flight: dict[str, Any],
) -> str | None:

    value = flight.get(
        "flightNumber"
    )

    if isinstance(
        value,
        dict,
    ):
        return (
            value.get("interpreted")
            or value.get("requested")
            or value.get("number")
        )

    if value is not None:
        return str(value)

    # Alternative structure
    value = flight.get(
        "flight"
    )

    if isinstance(
        value,
        dict,
    ):
        return (
            value.get("iata")
            or value.get("number")
            or value.get("interpreted")
            or value.get("requested")
        )

    if isinstance(
        value,
        str,
    ):
        return value

    return None


# ============================================================
# DEPARTURE PARSER
# ============================================================

def _get_departure(
    flight: dict[str, Any],
) -> tuple[str | None, str | None]:

    departure = (
        flight.get("departureAirport")
        or flight.get("departure")
        or {}
    )

    if not isinstance(
        departure,
        dict,
    ):
        departure = {}

    airport_code = (
        _get_airport_code_from_object(
            departure
        )
    )

    departure_time = (
        flight.get("departureTime")
        or flight.get("scheduledDeparture")
        or flight.get("departureDate")
        or _get_time_from_object(
            departure
        )
    )

    return (
        airport_code,
        departure_time,
    )


# ============================================================
# ARRIVAL PARSER
# ============================================================

def _get_arrival(
    flight: dict[str, Any],
) -> tuple[str | None, str | None]:

    arrival = (
        flight.get("arrivalAirport")
        or flight.get("arrival")
        or {}
    )

    if not isinstance(
        arrival,
        dict,
    ):
        arrival = {}

    airport_code = (
        _get_airport_code_from_object(
            arrival
        )
    )

    arrival_time = (
        flight.get("arrivalTime")
        or flight.get("scheduledArrival")
        or flight.get("arrivalDate")
        or _get_time_from_object(
            arrival
        )
    )

    return (
        airport_code,
        arrival_time,
    )


# ============================================================
# EXTRACT FLIGHTS
# ============================================================

def _extract_flights(
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract flight list from possible Cirium response structures.
    """

    # --------------------------------------------------------
    # Direct arrays
    # --------------------------------------------------------

    for key in (
        "scheduledFlights",
        "flights",
        "data",
    ):

        value = data.get(key)

        if isinstance(
            value,
            list,
        ):
            return [
                item
                for item in value
                if isinstance(
                    item,
                    dict,
                )
            ]

        if isinstance(
            value,
            dict,
        ):

            nested = _extract_flights(
                value
            )

            if nested:
                return nested

    # --------------------------------------------------------
    # Singular scheduledFlight
    # --------------------------------------------------------

    scheduled_flight = data.get(
        "scheduledFlight"
    )

    if isinstance(
        scheduled_flight,
        list,
    ):
        return [
            item
            for item in scheduled_flight
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        scheduled_flight,
        dict,
    ):
        return [
            scheduled_flight
        ]

    # --------------------------------------------------------
    # Nested response/result
    # --------------------------------------------------------

    for key in (
        "response",
        "results",
        "request",
    ):

        nested = data.get(key)

        if isinstance(
            nested,
            dict,
        ):

            result = _extract_flights(
                nested
            )

            if result:
                return result

        elif isinstance(
            nested,
            list,
        ):

            return [
                item
                for item in nested
                if isinstance(
                    item,
                    dict,
                )
            ]

    return []


# ============================================================
# NORMALIZE FLIGHT
# ============================================================

def _normalize_flight(
    flight: dict[str, Any],
    travelers: int,
    origin_code: str,
    destination_code: str,
) -> dict[str, Any]:

    airline_name, airline_code = (
        _get_airline(
            flight
        )
    )

    flight_number = (
        _get_flight_number(
            flight
        )
    )

    departure_airport, departure_time = (
        _get_departure(
            flight
        )
    )

    arrival_airport, arrival_time = (
        _get_arrival(
            flight
        )
    )

    # --------------------------------------------------------
    # Route fallback
    # --------------------------------------------------------

    if not departure_airport:
        departure_airport = origin_code

    if not arrival_airport:
        arrival_airport = destination_code

    # --------------------------------------------------------
    # Normalize airport codes
    # --------------------------------------------------------

    departure_airport = (
        departure_airport.upper()
        if departure_airport
        else origin_code
    )

    arrival_airport = (
        arrival_airport.upper()
        if arrival_airport
        else destination_code
    )

    # --------------------------------------------------------
    # Full flight number
    # --------------------------------------------------------

    full_flight_number = flight_number

    if (
        airline_code
        and flight_number
        and not str(
            flight_number
        ).upper().startswith(
            str(
                airline_code
            ).upper()
        )
    ):
        full_flight_number = (
            f"{airline_code}"
            f"{flight_number}"
        )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = (
        flight.get("status")
        or "scheduled"
    )

    if isinstance(
        status,
        dict,
    ):
        status = (
            status.get("status")
            or status.get("name")
            or "scheduled"
        )

    # --------------------------------------------------------
    # Normalized result
    # --------------------------------------------------------

    return {
        "flight_number": full_flight_number,
        "airline": (
            airline_name
            or "Unknown Airline"
        ),
        "airline_code": airline_code,

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

        "status": status,

        # Cirium Schedules API provides
        # flight schedule information.
        # It does not provide ticket fare here.
        "price": None,
        "currency": "INR",
        "travelers": travelers,

        "source": "cirium",
        "price_status": "not_available",
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
) -> list[dict[str, Any]]:

    # ========================================================
    # CIRIUM API KEY
    # ========================================================

    api_key = getattr(
        settings,
        "cirium_api_key",
        None,
    )

    if not api_key:
        print(
            "[cirium] ERROR: "
            "CIRIUM_API_KEY is missing."
        )

        return []

    api_key = str(
        api_key
    ).strip()

    if not api_key:
        print(
            "[cirium] ERROR: "
            "CIRIUM_API_KEY is empty."
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
            "[cirium] ERROR: "
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
            "[cirium] ERROR: "
            f"Unknown origin airport: {origin}"
        )

        return []

    if not destination_code:

        print(
            "[cirium] ERROR: "
            f"Unknown destination airport: "
            f"{destination}"
        )

        return []

    # ========================================================
    # SAME AIRPORT
    # ========================================================

    if origin_code == destination_code:

        print(
            "[cirium] ERROR: "
            "Origin and destination are identical."
        )

        return []

    # ========================================================
    # CIRIUM SCHEDULE ROUTE ENDPOINT
    # ========================================================

    url = (
        f"{CIRIUM_BASE_URL}"
        f"/schedules"
        f"/departure-airport/{origin_code}"
        f"/arrival-airport/{destination_code}"
        f"/departure-date/{requested_date}"
    )

    # ========================================================
    # QUERY PARAMETERS
    # ========================================================

    params = {
        "codeType": "IATA",
        "extendedOptions": (
            "useInlinedReferences,"
            "includeDirects,"
            "includeNewFields,"
            "languageCode:en"
        ),
    }

    # ========================================================
    # HEADERS
    # ========================================================

    headers = {
        "Accept": "application/json",
        "Authorization": api_key,
    }

    # ========================================================
    # DEBUG
    # ========================================================

    print("=" * 70)

    print(
        "[cirium] FLIGHT SCHEDULE SEARCH"
    )

    print(
        "[cirium] Origin:",
        origin,
        "=>",
        origin_code,
    )

    print(
        "[cirium] Destination:",
        destination,
        "=>",
        destination_code,
    )

    print(
        "[cirium] Departure date:",
        requested_date,
    )

    print(
        "[cirium] Travelers:",
        travelers_value,
    )

    print(
        "[cirium] Base URL:",
        CIRIUM_BASE_URL,
    )

    print(
        "[cirium] Endpoint:",
        url,
    )

    print(
        "[cirium] API key configured:",
        bool(api_key),
    )

    print("=" * 70)

    # ========================================================
    # HTTP REQUEST
    # ========================================================

    try:

        timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=10.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                url,
                headers=headers,
                params=params,
            )

        print(
            "[cirium] HTTP status:",
            response.status_code,
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if response.status_code == 200:

            print(
                "[cirium] API request successful."
            )

        # ====================================================
        # BAD REQUEST
        # ====================================================

        elif response.status_code == 400:

            print(
                "[cirium] ERROR 400: "
                "Invalid request."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # UNAUTHORIZED
        # ====================================================

        elif response.status_code == 401:

            print(
                "[cirium] ERROR 401: "
                "Invalid or missing API key."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # FORBIDDEN
        # ====================================================

        elif response.status_code == 403:

            print(
                "[cirium] ERROR 403: "
                "Request is forbidden."
            )

            print(
                "[cirium] This can mean:"
            )

            print(
                "  - API key is authenticated "
                "but endpoint is not enabled."
            )

            print(
                "  - Cirium plan does not allow "
                "scheduled flights by route."
            )

            print(
                "  - API quota was exceeded."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # NOT FOUND
        # ====================================================

        elif response.status_code == 404:

            print(
                "[cirium] ERROR 404: "
                "Endpoint or resource not found."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # NOT ACCEPTABLE
        # ====================================================

        elif response.status_code == 406:

            print(
                "[cirium] ERROR 406: "
                "Unsupported response format."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # RATE LIMIT
        # ====================================================

        elif response.status_code == 429:

            print(
                "[cirium] ERROR 429: "
                "Rate limit exceeded."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # SERVER ERROR
        # ====================================================

        elif response.status_code >= 500:

            print(
                "[cirium] ERROR:",
                response.status_code,
            )

            print(
                "[cirium] Cirium server error."
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

        # ====================================================
        # OTHER ERROR
        # ====================================================

        else:

            print(
                "[cirium] ERROR:",
                response.status_code,
            )

            print(
                "[cirium] Response:",
                response.text[:3000],
            )

            return []

    # ========================================================
    # TIMEOUT
    # ========================================================

    except httpx.TimeoutException:

        print(
            "[cirium] ERROR: "
            "Cirium request timed out."
        )

        return []

    # ========================================================
    # HTTP ERROR
    # ========================================================

    except httpx.HTTPError as error:

        print(
            "[cirium] HTTP error:",
            repr(error),
        )

        return []

    # ========================================================
    # UNKNOWN ERROR
    # ========================================================

    except Exception as error:

        print(
            "[cirium] Unexpected error:",
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
            "[cirium] ERROR: "
            "Response is not valid JSON."
        )

        print(
            "[cirium] Response:",
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
            "[cirium] ERROR: "
            "Unexpected response format."
        )

        return []

    # ========================================================
    # RESPONSE DEBUG
    # ========================================================

    print(
        "[cirium] Response keys:",
        list(
            data.keys()
        ),
    )

    # ========================================================
    # API ERROR
    # ========================================================

    if data.get("error"):

        print(
            "[cirium] API error:",
            data.get("error"),
        )

        return []

    # ========================================================
    # EXTRACT RAW FLIGHTS
    # ========================================================

    raw_flights = _extract_flights(
        data
    )

    print(
        "[cirium] Raw flight count:",
        len(raw_flights),
    )

    # ========================================================
    # NORMALIZE
    # ========================================================

    results: list[
        dict[str, Any]
    ] = []

    seen: set[str] = set()

    for flight in raw_flights:

        normalized = _normalize_flight(
            flight=flight,
            travelers=travelers_value,
            origin_code=origin_code,
            destination_code=destination_code,
        )

        # ----------------------------------------------------
        # Ignore completely invalid records
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
            f"{normalized.get('departure_time')}"
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            normalized
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "[cirium] Final flight count:",
        len(results),
    )

    if results:

        print(
            "[cirium] First flight:",
            results[0],
        )

    else:

        print(
            "[cirium] No scheduled flights returned."
        )

    print("=" * 70)

    return results[:20]