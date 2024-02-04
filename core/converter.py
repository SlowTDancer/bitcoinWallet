from typing import Any

import requests

from core.errors import ConversionError


def get_btc_to_usd_rate() -> Any:
    url = "https://blockchain.info/ticker"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data['USD']['last']

    raise ConversionError()
