import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

from constants import BITCOIN
from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


def create_user_and_wallets(client: TestClient) -> tuple[Any, ...]:
    email = "test@example.com"
    user_request_data = {"email": email}

    user_response = client.post("/users", json=user_request_data)

    wallet_response1 = client.post("/wallets", headers=user_response.json()["user"])
    wallet_response2 = client.post("/wallets", headers=user_response.json()["user"])

    return user_response, wallet_response1, wallet_response2


def test_make_transaction_success(client: TestClient) -> None:
    user_response, wallet_response1, wallet_response2 = create_user_and_wallets(client)
    public_key1 = wallet_response1.json()["wallet"]["public_key"]
    public_key2 = wallet_response2.json()["wallet"]["public_key"]

    transaction_request_data = {
        "from_key": public_key1,
        "to_key": public_key2,
        "amount": 1,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers=user_response.json()["user"],
    )

    assert response.status_code == 201
    assert "transaction" in response.json()


def test_make_transaction_user_does_not_exist(client: TestClient) -> None:
    transaction_request_data = {
        "from_key": str(uuid.uuid4()),
        "to_key": str(uuid.uuid4()),
        "amount": 100,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers={"api_key": str(uuid.uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "User does not exist."


def test_make_transaction_wallet_does_not_exist(client: TestClient) -> None:
    user_response, _, _ = create_user_and_wallets(client)
    wallet_address = str(uuid.uuid4())

    transaction_request_data = {
        "from_key": wallet_address,
        "to_key": wallet_address,
        "amount": 100,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers=user_response.json()["user"],
    )

    assert response.status_code == 405
    assert (
        response.json()["error"]["message"]
        == f"Wallet with address <{wallet_address}> does not exist."
    )


def test_make_transaction_same_wallets(client: TestClient) -> None:
    user_response, wallet_response, _ = create_user_and_wallets(client)
    public_key = wallet_response.json()["wallet"]["public_key"]

    transaction_request_data = {
        "from_key": public_key,
        "to_key": public_key,
        "amount": 1,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers=user_response.json()["user"],
    )

    assert response.status_code == 420
    assert response.json()["error"]["message"] == (
        "You are trying to make transaction from "
        f"wallet with address <{public_key}> to "
        f"same wallet with address <{public_key}>."
    )


def test_make_transaction_not_enough_balance(client: TestClient) -> None:
    user_response, wallet_response1, wallet_response2 = create_user_and_wallets(client)
    public_key1 = wallet_response1.json()["wallet"]["public_key"]

    transaction_request_data = {
        "from_key": public_key1,
        "to_key": wallet_response2.json()["wallet"]["public_key"],
        "amount": 100 * BITCOIN,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers=user_response.json()["user"],
    )

    assert response.status_code == 419
    assert (
        response.json()["error"]["message"]
        == f"Wallet with address <{public_key1}> does not have enough balance."
    )


def test_can_not_make_non_positive_transaction(client: TestClient) -> None:
    user_response, wallet_response1, wallet_response2 = create_user_and_wallets(client)
    public_key1 = wallet_response1.json()["wallet"]["public_key"]

    transaction_request_data = {
        "from_key": public_key1,
        "to_key": wallet_response2.json()["wallet"]["public_key"],
        "amount": 0,
    }
    response = client.post(
        "/transactions",
        json=transaction_request_data,
        headers=user_response.json()["user"],
    )

    assert response.status_code == 413
    assert (
        response.json()["error"]["message"]
        == "Transaction amount must be a positive integer."
    )


def test_get_transactions_success(client: TestClient) -> None:
    user_response, _, _ = create_user_and_wallets(client)

    response = client.get("/transactions", headers=user_response.json()["user"])

    assert response.status_code == 200
    assert "transactions" in response.json()


def test_get_transactions_user_does_not_exist(client: TestClient) -> None:
    response = client.get("/transactions", headers={"api_key": str(uuid.uuid4())})

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "User does not exist."
