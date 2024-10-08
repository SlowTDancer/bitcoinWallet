from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse

from constants import BITCOIN, ERROR_RESPONSES
from core.converter import get_btc_to_usd_rate
from core.errors import (
    ConversionError,
    InvalidOwnerError,
    UserDoesNotExistError,
    WalletDoesNotExistError,
    WalletLimitReachedError,
)
from core.wallet import Wallet
from infra.fastapi.dependables import (
    UserRepositoryDependable,
    WalletRepositoryDependable,
)

wallet_api = APIRouter(tags=["Wallets"])


class WalletItemResponse(BaseModel):
    public_key: UUID
    btc_balance: float
    usd_balance: float


class TransactionItemResponse(BaseModel):
    to_key: UUID
    from_key: UUID
    amount: float

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TransactionItemResponse):
            return (
                self.to_key == other.to_key
                and self.from_key == other.from_key
                and self.amount == other.amount
            )
        return False


class TransactionItemResponseEnvelope(BaseModel):
    transaction: TransactionItemResponse


class TransactionListResponseEnvelope(BaseModel):
    transactions: list[TransactionItemResponse]


class WalletItemResponseEnvelope(BaseModel):
    wallet: WalletItemResponse


@wallet_api.post(
    "/wallets",
    status_code=201,
    response_model=WalletItemResponseEnvelope,
    responses={
        404: ERROR_RESPONSES[404],
        410: ERROR_RESPONSES[410],
        415: ERROR_RESPONSES[415],
    },
)
def create_wallet(
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    wallet = Wallet(private_key=api_key)
    try:
        user = users.get(api_key)
    except UserDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "User does not exist."}},
        )

    try:
        users.add_wallet(api_key, wallet.get_public_key())
        wallets.create(wallet)
        btc_balance = wallet.get_balance() / BITCOIN
        usd_balance = get_btc_to_usd_rate() * btc_balance
        response = WalletItemResponse(
            public_key=wallet.get_public_key(),
            btc_balance=btc_balance,
            usd_balance=usd_balance,
        )
        return {"wallet": response}
    except WalletLimitReachedError:
        return JSONResponse(
            status_code=410,
            content={
                "error": {
                    "message": f"User's with email <{user.get_email()}> wallet "
                    "quantity limit is reached."
                }
            },
        )
    except ConversionError:
        return JSONResponse(
            status_code=415,
            content={"error": {"message": "conversion of btc to usd failed."}},
        )


@wallet_api.get(
    "/wallets/{address}",
    status_code=200,
    response_model=WalletItemResponseEnvelope,
    responses={
        404: ERROR_RESPONSES[404],
        405: ERROR_RESPONSES[405],
        409: ERROR_RESPONSES[409],
        415: ERROR_RESPONSES[415],
    },
)
def get_wallet_by_address(
    address: UUID,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.get(api_key)
    except UserDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "User does not exist."}},
        )
    try:
        wallet = wallets.get_wallet(api_key, address)
        btc_balance = wallet.get_balance() / BITCOIN
        usd_balance = get_btc_to_usd_rate() * btc_balance
        response = WalletItemResponse(
            public_key=address, btc_balance=btc_balance, usd_balance=usd_balance
        )
        return {"wallet": response}
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {"message": f"Wallet with address <{address}> does not exist."}
            },
        )
    except InvalidOwnerError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "message": f"Wallet with address <{address}> "
                    "does not belong to the correct owner."
                }
            },
        )
    except ConversionError:
        return JSONResponse(
            status_code=415,
            content={"error": {"message": "conversion of btc to usd failed."}},
        )


@wallet_api.get(
    "/wallets/{address}/transactions",
    status_code=200,
    response_model=TransactionListResponseEnvelope,
    responses={
        404: ERROR_RESPONSES[404],
        405: ERROR_RESPONSES[405],
        409: ERROR_RESPONSES[409],
    },
)
def get_wallet_transactions(
    address: UUID,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.get(api_key)
    except UserDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "User does not exist."}},
        )
    try:
        wallet_transactions = wallets.get_transactions(api_key, address)
        return {
            "transactions": [
                TransactionItemResponse(
                    to_key=transaction.get_to_key(),
                    from_key=transaction.get_from_key(),
                    amount=transaction.get_amount() / BITCOIN,
                )
                for transaction in wallet_transactions
            ]
        }
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {"message": f"Wallet with address <{address}> does not exist."}
            },
        )
    except InvalidOwnerError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "message": f"Wallet with address <{address}> "
                    "does not belong to the correct owner."
                }
            },
        )
