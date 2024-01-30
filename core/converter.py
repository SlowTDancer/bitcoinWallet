from typing import Any

import requests

from core.errors import ConversionError


def get_btc_to_usd_rate() -> Any:
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {"ids": "bitcoin", "vs_currencies": "usd"}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data["bitcoin"]["usd"]

    raise ConversionError()
