from typing import Any

import requests

from constants import CONVERTER_URL
from core.errors import ConversionError


def get_btc_to_usd_rate() -> Any:
    url = CONVERTER_URL

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["USD"]["last"]

    raise ConversionError()
