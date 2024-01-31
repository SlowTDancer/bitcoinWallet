from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from core.converter import get_btc_to_usd_rate
from core.errors import ConversionError


@pytest.fixture
def mock_requests_get() -> Generator[MagicMock, None, None]:
    with patch("requests.get") as mock_get:
        yield mock_get


def test_successful_request(mock_requests_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"bitcoin": {"usd": 50000}}
    mock_requests_get.return_value = mock_response

    result = get_btc_to_usd_rate()

    assert result == 50000


def test_failed_request(mock_requests_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    with pytest.raises(ConversionError):
        get_btc_to_usd_rate()
