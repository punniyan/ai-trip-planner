# app/tools/currency.py

from typing import Any

import httpx

from app.config import settings


# ============================================================
# DEFAULT APIs
# ============================================================

FRANKFURTER_DEFAULT_URL = (
    "https://api.frankfurter.app"
)

EXCHANGE_RATE_DEFAULT_URL = (
    "https://open.er-api.com/v6/latest"
)


# ============================================================
# SAFE FLOAT
# ============================================================

def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


# ============================================================
# RESULT BUILDER
# ============================================================

def _build_result(
    amount: float,
    from_currency: str,
    to_currency: str,
    converted_amount: float | None,
    rate: float | None,
    source: str,
    error: str | None = None,
) -> dict[str, Any]:

    result = {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": (
            round(converted_amount, 2)
            if converted_amount is not None
            else None
        ),
        "rate": (
            round(rate, 8)
            if rate is not None
            else None
        ),
        "source": source,
    }

    if error:
        result["error"] = error

    return result


# ============================================================
# CONVERT CURRENCY
# ============================================================

async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:

    # --------------------------------------------------------
    # Normalize amount
    # --------------------------------------------------------

    amount_value = _safe_float(amount)

    if amount_value is None:
        amount_value = 0.0

    # --------------------------------------------------------
    # Normalize currencies
    # --------------------------------------------------------

    from_currency_value = (
        str(from_currency or "INR")
        .strip()
        .upper()
    )

    to_currency_value = (
        str(to_currency or "INR")
        .strip()
        .upper()
    )

    # --------------------------------------------------------
    # Same currency
    # --------------------------------------------------------

    if from_currency_value == to_currency_value:

        return _build_result(
            amount=amount_value,
            from_currency=from_currency_value,
            to_currency=to_currency_value,
            converted_amount=amount_value,
            rate=1.0,
            source="same_currency",
        )

    print(
        "[currency] Conversion:",
        amount_value,
        from_currency_value,
        "->",
        to_currency_value,
    )

    # ========================================================
    # METHOD 1
    # FRANKFURTER
    # ========================================================

    currency_api_url = getattr(
        settings,
        "currency_api_url",
        None,
    )

    base_url = (
        currency_api_url
        or FRANKFURTER_DEFAULT_URL
    ).rstrip("/")

    frankfurter_url = f"{base_url}/latest"

    frankfurter_params = {
        "amount": amount_value,
        "from": from_currency_value,
        "to": to_currency_value,
    }

    try:

        async with httpx.AsyncClient(timeout=20.0) as client:

            response = await client.get(
                frankfurter_url,
                params=frankfurter_params,
            )

            print(
                "[currency] Frankfurter status:",
                response.status_code,
            )

            if response.status_code == 200:

                data = response.json()

                if isinstance(data, dict):

                    rates = data.get(
                        "rates",
                        {},
                    )

                    if isinstance(rates, dict):

                        converted = _safe_float(
                            rates.get(
                                to_currency_value
                            )
                        )

                        if converted is not None:

                            rate = (
                                converted / amount_value
                                if amount_value != 0
                                else 0.0
                            )

                            return _build_result(
                                amount=amount_value,
                                from_currency=from_currency_value,
                                to_currency=to_currency_value,
                                converted_amount=converted,
                                rate=rate,
                                source="frankfurter",
                            )

    except Exception as error:

        print(
            "[currency] Frankfurter failed:",
            error,
        )

    # ========================================================
    # METHOD 2
    # OPEN EXCHANGE RATE API
    # ========================================================

    fallback_base_url = (
        getattr(
            settings,
            "exchange_rate_api_url",
            None,
        )
        or EXCHANGE_RATE_DEFAULT_URL
    ).rstrip("/")

    fallback_url = (
        f"{fallback_base_url}/"
        f"{from_currency_value}"
    )

    try:

        async with httpx.AsyncClient(timeout=20.0) as client:

            response = await client.get(
                fallback_url
            )

            print(
                "[currency] ExchangeRate API status:",
                response.status_code,
            )

            response.raise_for_status()

            data = response.json()

        if not isinstance(data, dict):

            raise ValueError(
                "Invalid exchange rate response."
            )

        if data.get("result") != "success":

            raise ValueError(
                data.get(
                    "error-type",
                    "Currency API failed.",
                )
            )

        rates = data.get(
            "rates",
            {},
        )

        if not isinstance(rates, dict):

            raise ValueError(
                "Rates data missing."
            )

        rate = _safe_float(
            rates.get(
                to_currency_value
            )
        )

        if rate is None:

            return _build_result(
                amount=amount_value,
                from_currency=from_currency_value,
                to_currency=to_currency_value,
                converted_amount=None,
                rate=None,
                source="exchange_rate_api",
                error=(
                    f"Rate not found for "
                    f"{from_currency_value} -> "
                    f"{to_currency_value}"
                ),
            )

        converted_amount = (
            amount_value * rate
        )

        return _build_result(
            amount=amount_value,
            from_currency=from_currency_value,
            to_currency=to_currency_value,
            converted_amount=converted_amount,
            rate=rate,
            source="exchange_rate_api",
        )

    except Exception as error:

        print(
            "[currency] ExchangeRate API failed:",
            error,
        )

    # ========================================================
    # FINAL FAILURE
    # ========================================================

    return _build_result(
        amount=amount_value,
        from_currency=from_currency_value,
        to_currency=to_currency_value,
        converted_amount=None,
        rate=None,
        source="currency_api",
        error=(
            f"Unable to convert "
            f"{from_currency_value} -> "
            f"{to_currency_value}"
        ),
    )