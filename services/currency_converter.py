import requests


FRANKFURTER_API_URL = "https://api.frankfurter.dev/v2/rates"


def convert_currency(amount, from_currency, to_currency):
    amount = float(amount)
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    if from_currency == to_currency:
        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0,
            "converted_amount": amount,
            "date": "same currency"
        }

    response = requests.get(
        FRANKFURTER_API_URL,
        params={
            "base": from_currency,
            "quotes": to_currency
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError(
            f"No exchange rate found for "
            f"{from_currency} to {to_currency}"
        )

    rate_data = data[0]

    rate = float(rate_data["rate"])
    converted_amount = amount * rate

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": rate,
        "converted_amount": converted_amount,
        "date": rate_data["date"]
    }
