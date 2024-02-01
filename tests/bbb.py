import pytest
from fastapi.testclient import TestClient
from uuid import UUID

from core.wallet import Wallet
from runner.setup import init_app


@pytest.fixture
def test_client():
    return TestClient(init_app())


def test_create_wallet_success(test_client):
    private_key = UUID("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    request_data = {"private_key": private_key}
    expected_public_key = UUID("12345678-9012-3456-7890-abcdef123456")

    response = test_client.post("/wallets", json=request_data)

    assert response.status_code == 201
    assert response.json() == {
        "wallet": {
            "public_key": str(expected_public_key),
            "btc_balance": 0.0,
            "usd_balance": 0.0,
        }
    }


def test_get_wallet_by_address_success(test_client):
    private_key = UUID("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    wallet_address = UUID("12345678-9012-3456-7890-abcdef123456")
    expected_wallet = Wallet(private_key=private_key, public_key=wallet_address)

    response = test_client.get(f"/wallets/{wallet_address}")

    assert response.status_code == 200
    assert response.json() == {
        "wallet": {
            "public_key": str(wallet_address),
            "btc_balance": 0.0,
            "usd_balance": 0.0,
        }
    }


def test_get_wallet_transactions_success(test_client):
    private_key = UUID("a1b2c3d4-e5f6-7890-1234-567890abcdef")
    wallet_address = UUID("12345678-9012-3456-7890-abcdef123456")
    expected_transactions = [
        {"to_key": UUID("11111111-2222-3333-4444-555555555555"), "from_key": wallet_address, "amount": 1.0},
        {"to_key": UUID("55555555-4444-3333-2222-111111111111"), "from_key": wallet_address, "amount": 2.0},
    ]

    response = test_client.get(f"/wallets/{wallet_address}/transactions")

    assert response.status_code == 200
    assert response.json() == {
        "transactions": [
            {"to_key": str(item["to_key"]), "from_key": str(item["from_key"]), "amount": item["amount"]}
            for item in expected_transactions
        ]
    }

