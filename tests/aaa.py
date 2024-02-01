import pytest
from fastapi.testclient import TestClient

from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_register_user_success(client: TestClient):
    email = "test@example.com"
    request_data = {"email": email}
    # expected_private_key = "a1b2c3d4-e5f6-7890-1234-567890abcdef"

    response = client.post("/users", json=request_data)

    assert response.status_code == 201
    # assert response.json() == {"Private Key": expected_private_key}


def test_register_user_conflict(client: TestClient):
    email = "test@example.com"
    request_data = {"email": email}

    response = client.post("/users", json=request_data)

    assert response.status_code == 409
    expected_error_message = f"user with email <{email}> already exists."
    assert response.json() == {"error": {"message": expected_error_message}}
