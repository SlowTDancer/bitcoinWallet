from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from constants import ADMIN_API_KEY
from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_get_statistics_success(client: TestClient) -> None:
    api_key = ADMIN_API_KEY

    response = client.get("/statistics", headers={"api_key": str(api_key)})

    assert response.status_code == 200
    assert "statistics" in response.json()
    assert response.json() == {
        "statistics": {"transactions_number": 0, "platform_profit": 0.0}
    }


def test_get_statistics_invalid_admin_key(client: TestClient) -> None:
    invalid_api_key = uuid4()

    response = client.get("/statistics", headers={"api_key": str(invalid_api_key)})

    assert response.status_code == 401
    assert response.json() == {"error": {"message": f"Invalid admin API key <{invalid_api_key}>"}}
