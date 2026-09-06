from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _safe_number(value: Any, default: float = 0.0) -> float:
    """
    Convert a value into a safe positive float.
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return default

    try:
        number = float(value)

        if number < 0:
            return default

        return number

    except (TypeError, ValueError):
        return default


def _get_price(item: dict[str, Any], *keys: str) -> float | None:
    """
    Find the first valid price from the given keys.
    """

    if not isinstance(item, dict):
        return None

    for key in keys:
        if key not in item:
            continue

        value = item.get(key)

        if value is None:
            continue

        price = _safe_number(value, -1)

        if price >= 0:
            return price

    return None


def _normalize_list(value: Any) -> list:
    """
    Make sure a value is always a list.
    """

    return value if isinstance(value, list) else []


def _normalize_int(value: Any, default: int = 1) -> int:
    """
    Convert value into a positive integer.
    """

    try:
        number = int(value)

        if number < 1:
            return default

        return number

    except (TypeError, ValueError):
        return default


# ============================================================
# FOOD CALCULATION
# ============================================================

def _calculate_food_cost(
    restaurants: list[dict[str, Any]],
    itinerary: list[dict[str, Any]],
    travelers: int,
    days: int,
    food_per_person_per_day: float = 1000,
) -> dict[str, Any]:
    """
    Calculate food cost.

    Priority:
    1. Use prices from selected itinerary restaurants.
    2. If itinerary prices are unavailable, use restaurant API prices.
    3. If no real restaurant price is available, use estimated
       per-person-per-day cost.

    IMPORTANT:
    Estimated amount is never treated as an actual API price.
    """

    travelers = _normalize_int(travelers, 1)
    days = _normalize_int(days, 1)

    # --------------------------------------------------------
    # 1. Check itinerary restaurant prices
    # --------------------------------------------------------

    itinerary_prices: list[float] = []

    for day in itinerary:
        if not isinstance(day, dict):
            continue

        activities = day.get("activities", [])

        if not isinstance(activities, list):
            continue

        for activity in activities:
            if not isinstance(activity, dict):
                continue

            activity_type = str(
                activity.get("type", "")
            ).strip().lower()

            # Restaurant activity
            if activity_type not in {
                "restaurant",
                "food",
                "dining",
            }:
                continue

            price = _get_price(
                activity,
                "price",
                "meal_price",
                "average_price",
                "cost",
            )

            if price is not None and price > 0:
                itinerary_prices.append(price)

    if itinerary_prices:

        average_meal_price = (
            sum(itinerary_prices) / len(itinerary_prices)
        )

        total = (
            average_meal_price
            * travelers
            * days
        )

        return {
            "amount": round(total, 2),
            "currency": "INR",
            "price_status": "actual",
            "calculation": (
                f"Average restaurant price "
                f"{round(average_meal_price, 2)} × "
                f"{travelers} travelers × "
                f"{days} days"
            ),
            "source": "itinerary_restaurant_prices",
            "estimated": False,
        }

    # --------------------------------------------------------
    # 2. Check restaurant API prices
    # --------------------------------------------------------

    restaurant_prices: list[float] = []

    for restaurant in restaurants:

        if not isinstance(restaurant, dict):
            continue

        price = _get_price(
            restaurant,
            "price",
            "meal_price",
            "average_price",
            "cost",
            "price_per_person",
        )

        if price is not None and price > 0:
            restaurant_prices.append(price)

    if restaurant_prices:

        average_meal_price = (
            sum(restaurant_prices)
            / len(restaurant_prices)
        )

        total = (
            average_meal_price
            * travelers
            * days
        )

        return {
            "amount": round(total, 2),
            "currency": "INR",
            "price_status": "actual",
            "calculation": (
                f"Average restaurant API price "
                f"{round(average_meal_price, 2)} × "
                f"{travelers} travelers × "
                f"{days} days"
            ),
            "source": "restaurant_api",
            "estimated": False,
        }

    # --------------------------------------------------------
    # 3. No real price → estimated
    # --------------------------------------------------------

    total = (
        food_per_person_per_day
        * travelers
        * days
    )

    return {
        "amount": round(total, 2),
        "currency": "INR",
        "price_status": "estimated",
        "calculation": (
            f"Estimated food cost "
            f"{food_per_person_per_day} per person/day × "
            f"{travelers} travelers × "
            f"{days} days"
        ),
        "source": "default_food_estimate",
        "estimated": True,
    }


# ============================================================
# TRANSPORT CALCULATION
# ============================================================

def _calculate_transport_cost(
    days: int,
    transport_per_day: float = 500,
) -> dict[str, Any]:
    """
    Calculate local transportation cost.

    Currently there is no live transportation pricing API
    connected to the project.

    Therefore this amount is explicitly marked as estimated.
    """

    days = _normalize_int(days, 1)

    total = transport_per_day * days

    return {
        "amount": round(total, 2),
        "currency": "INR",
        "price_status": "estimated",
        "calculation": (
            f"Estimated transport cost "
            f"{transport_per_day} per day × "
            f"{days} days"
        ),
        "source": "default_transport_estimate",
        "estimated": True,
    }


# ============================================================
# MAIN BUDGET CALCULATION
# ============================================================

def calculate_budget(
    flights: list[dict[str, Any]] | None = None,
    hotels: list[dict[str, Any]] | None = None,
    restaurants: list[dict[str, Any]] | None = None,
    attractions: list[dict[str, Any]] | None = None,
    itinerary: list[dict[str, Any]] | None = None,
    travelers: int = 1,
    days: int = 1,
    transport_per_day: float = 500,
    food_per_person_per_day: float = 1000,
    budget_limit: float | None = None,
    currency: str = "INR",
) -> dict[str, Any]:

    # ========================================================
    # NORMALIZE INPUTS
    # ========================================================

    flights = _normalize_list(flights)
    hotels = _normalize_list(hotels)
    restaurants = _normalize_list(restaurants)
    attractions = _normalize_list(attractions)
    itinerary = _normalize_list(itinerary)

    travelers = _normalize_int(travelers, 1)
    days = _normalize_int(days, 1)

    currency = str(currency or "INR").upper()

    # ========================================================
    # NIGHTS
    # ========================================================

    # Example:
    # 4 days = 3 nights
    # 1 day  = 0 nights

    nights = max(days - 1, 0)

    # ========================================================
    # FLIGHT COST
    # ========================================================

    flight_prices: list[float] = []

    for flight in flights:

        price = _get_price(
            flight,
            "price",
            "fare",
            "ticket_price",
            "total_price",
        )

        if price is not None and price > 0:
            flight_prices.append(price)

    if flight_prices:

        flight_price = min(flight_prices)

        flight_total = (
            flight_price * travelers
        )

        flight_status = "actual"

    else:

        flight_total = 0.0
        flight_status = "unavailable"

    # ========================================================
    # HOTEL COST
    # ========================================================

    hotel_prices: list[float] = []

    for hotel in hotels:

        price = _get_price(
            hotel,
            "price",
            "price_per_night",
            "nightly_price",
            "room_price",
            "rate",
        )

        if price is not None and price > 0:
            hotel_prices.append(price)

    if hotel_prices and nights > 0:

        hotel_price = min(hotel_prices)

        hotel_total = (
            hotel_price * nights
        )

        hotel_status = "actual"

    elif nights == 0:

        hotel_total = 0.0
        hotel_status = "not_required"

    else:

        hotel_total = 0.0
        hotel_status = "unavailable"

    # ========================================================
    # FOOD COST
    # ========================================================

    food = _calculate_food_cost(
        restaurants=restaurants,
        itinerary=itinerary,
        travelers=travelers,
        days=days,
        food_per_person_per_day=food_per_person_per_day,
    )

    food_total = food["amount"]

    # ========================================================
    # ACTIVITY COST
    # ========================================================

    activity_prices: list[float] = []

    # --------------------------------------------------------
    # First use attractions actually selected in itinerary
    # --------------------------------------------------------

    for day in itinerary:

        if not isinstance(day, dict):
            continue

        activities = day.get("activities", [])

        if not isinstance(activities, list):
            continue

        for activity in activities:

            if not isinstance(activity, dict):
                continue

            activity_type = str(
                activity.get("type", "")
            ).strip().lower()

            if activity_type not in {
                "attraction",
                "place",
                "activity",
            }:
                continue

            price = _get_price(
                activity,
                "ticket_price",
                "price",
                "entry_fee",
                "entrance_fee",
            )

            if price is not None and price > 0:
                activity_prices.append(price)

    # --------------------------------------------------------
    # If itinerary does not contain prices,
    # check original attraction API data
    # --------------------------------------------------------

    if not activity_prices:

        for attraction in attractions:

            if not isinstance(attraction, dict):
                continue

            price = _get_price(
                attraction,
                "ticket_price",
                "price",
                "entry_fee",
                "entrance_fee",
            )

            if price is not None and price > 0:
                activity_prices.append(price)

    if activity_prices:

        activity_total = (
            sum(activity_prices)
            * travelers
        )

        activity_status = "actual"

    else:

        activity_total = 0.0
        activity_status = "unavailable"

    # ========================================================
    # TRANSPORT
    # ========================================================

    transport = _calculate_transport_cost(
        days=days,
        transport_per_day=transport_per_day,
    )

    transport_total = transport["amount"]

    # ========================================================
    # TOTAL
    # ========================================================

    total = (
        flight_total
        + hotel_total
        + food_total
        + activity_total
        + transport_total
    )

    # ========================================================
    # BUDGET LIMIT
    # ========================================================

    remaining = None
    within_budget = None

    if budget_limit is not None:

        budget_limit = _safe_number(
            budget_limit,
            0.0,
        )

        remaining = round(
            budget_limit - total,
            2,
        )

        within_budget = (
            total <= budget_limit
        )

    # ========================================================
    # UNAVAILABLE / ESTIMATED
    # ========================================================

    unavailable: list[str] = []
    estimated: list[str] = []

    if flight_status == "unavailable":
        unavailable.append("flights")

    if hotel_status == "unavailable":
        unavailable.append("hotels")

    if activity_status == "unavailable":
        unavailable.append("activities")

    if food["estimated"]:
        estimated.append("food")

    if transport["estimated"]:
        estimated.append("transport")

    # ========================================================
    # PRICE STATUS
    # ========================================================

    actual_components = 0
    total_components = 5

    if flight_status == "actual":
        actual_components += 1

    if hotel_status == "actual":
        actual_components += 1

    if food["price_status"] == "actual":
        actual_components += 1

    if activity_status == "actual":
        actual_components += 1

    # Transport is currently always estimated
    # because there is no live transport pricing API.
    if transport["price_status"] == "actual":
        actual_components += 1

    # ========================================================
    # COMPLETENESS
    # ========================================================

    completeness_percentage = round(
        (
            actual_components
            / total_components
        ) * 100,
        2,
    )

    if completeness_percentage == 100:

        completeness = "complete"

    elif completeness_percentage >= 60:

        completeness = "mostly_complete"

    else:

        completeness = "partial"

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "currency": currency,

        "flights": {
            "amount": round(flight_total, 2),
            "price_status": flight_status,
            "estimated": False,
        },

        "hotels": {
            "amount": round(hotel_total, 2),
            "price_status": hotel_status,
            "estimated": False,
            "nights": nights,
        },

        "food": {
            "amount": round(food_total, 2),
            "price_status": food["price_status"],
            "estimated": food["estimated"],
            "calculation": food["calculation"],
            "source": food["source"],
        },

        "activities": {
            "amount": round(activity_total, 2),
            "price_status": activity_status,
            "estimated": False,
        },

        "transport": {
            "amount": round(transport_total, 2),
            "price_status": transport["price_status"],
            "estimated": transport["estimated"],
            "calculation": transport["calculation"],
            "source": transport["source"],
        },

        "total": round(total, 2),

        "budget_limit": (
            round(budget_limit, 2)
            if budget_limit is not None
            else None
        ),

        "remaining": remaining,

        "within_budget": within_budget,

        "unavailable": unavailable,

        "estimated": estimated,

        "completeness": completeness,

        "completeness_percentage": completeness_percentage,

        "travelers": travelers,

        "days": days,

        "nights": nights,
    }