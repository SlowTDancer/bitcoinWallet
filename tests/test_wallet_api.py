import uuid

import pytest
from fastapi.testclient import TestClient

from constants import MAX_WALLETS_PER_USER
from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def test_create_wallet_success(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    response = client.post("/wallets", headers=user_response.json()["user"])

    assert response.status_code == 201
    assert "wallet" in response.json()


def test_create_wallet_user_not_found(client: TestClient) -> None:
    request = {"api_key": str(uuid.uuid4())}

    response = client.post("/wallets", headers=request)

    assert response.status_code == 404
    assert response.json() == {"error": {"message": "User does not exist."}}


def test_create_wallet_wallet_limit_reached(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    for i in range(MAX_WALLETS_PER_USER):
        client.post("/wallets", headers=user_response.json()["user"])

    response = client.post("/wallets", headers=user_response.json()["user"])

    assert response.status_code == 410
    assert response.json() == {
        "error": {
            "message": f"User's with email <{email}> wallet quantity limit is reached."
        }
    }


def test_get_wallet_by_address_success(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    wallet_response = client.post("/wallets", headers=user_response.json()["user"])

    public_key = wallet_response.json()["wallet"].get("public_key")

    response = client.get(
        f"/wallets/{str(public_key)}", headers=user_response.json()["user"]
    )

    assert response.status_code == 200
    assert "wallet" in response.json()


def test_get_wallet_by_address_user_not_found(client: TestClient) -> None:
    response = client.get(
        f"/wallets/{str(uuid.uuid4())}",
        headers={"api_key": f"{str(uuid.uuid4())}"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": {"message": "User does not exist."}}


def test_get_wallet_by_address_wallet_not_found(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    address = str(uuid.uuid4())

    response = client.get(
        f"/wallets/{address}",
        headers=user_response.json()["user"],
    )

    assert response.status_code == 405
    assert response.json() == {
        "error": {"message": f"Wallet with address <{address}> does not exist."}
    }


def test_get_wallet_by_address_invalid_owner(client: TestClient) -> None:
    email1 = "test@example.com"
    request_data1 = {"email": email1}
    user_response1 = client.post("/users", json=request_data1)

    wallet_response = client.post("/wallets", headers=user_response1.json()["user"])

    email2 = "testing@example.com"
    request_data2 = {"email": email2}
    user_response2 = client.post("/users", json=request_data2)

    public_key = wallet_response.json()["wallet"].get("public_key")

    response = client.get(
        f"/wallets/{str(public_key)}",
        headers=user_response2.json()["user"],
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "message": f"Wallet with address <{str(public_key)}> "
            "does not belong to the correct owner."
        }
    }


def test_get_wallet_transactions_success(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    wallet_response = client.post("/wallets", headers=user_response.json()["user"])

    public_key = wallet_response.json()["wallet"].get("public_key")
    response = client.get(
        f"/wallets/{str(public_key)}/transactions",
        headers=user_response.json()["user"],
    )

    assert response.status_code == 200
    assert "transactions" in response.json()


def test_get_wallet_transactions_user_not_found(client: TestClient) -> None:
    address = str(uuid.uuid4())

    response = client.get(
        f"/wallets/{address}/transactions",
        headers={"api_key": f"{str(uuid.uuid4())}"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": {"message": "User does not exist."}}


def test_get_wallet_transactions_wallet_not_found(client: TestClient) -> None:
    email = "test@example.com"
    request_data = {"email": email}
    user_response = client.post("/users", json=request_data)

    address = str(uuid.uuid4())

    response = client.get(
        f"/wallets/{address}/transactions",
        headers=user_response.json()["user"],
    )

    assert response.status_code == 405
    assert response.json() == {
        "error": {"message": f"Wallet with address <{address}> does not exist."}
    }


def test_get_wallet_transactions_invalid_owner(client: TestClient) -> None:
    email1 = "test@example.com"
    request_data1 = {"email": email1}
    user_response1 = client.post("/users", json=request_data1)

    wallet_response = client.post("/wallets", headers=user_response1.json()["user"])

    email2 = "test2@example.com"
    request_data2 = {"email": email2}
    user_response2 = client.post("/users", json=request_data2)

    public_key = wallet_response.json()["wallet"].get("public_key")

    response = client.get(
        f"/wallets/{str(public_key)}/transactions",
        headers=user_response2.json()["user"],
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "message": f"Wallet with address <{str(public_key)}> "
            "does not belong to the correct owner."
        }
    }
