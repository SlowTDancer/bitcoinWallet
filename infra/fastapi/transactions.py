from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import (
    InvalidOwnerError,
    NotEnoughBalanceError,
    SameWalletsError,
    WalletDoesNotExistError,
)
from core.transaction import Transaction
from infra.fastapi.dependables import WalletRepositoryDependable
from infra.fastapi.wallets import (
    TransactionItemResponse,
    TransactionItemResponseEnvelope,
    TransactionListResponseEnvelope,
)

transaction_api = APIRouter(tags=["Transactions"])


class MakeTransactionRequest(BaseModel):
    private_key: UUID
    from_key: UUID
    to_key: UUID
    amount: float


@transaction_api.post(
    "/transactions",
    status_code=201,
    response_model=TransactionItemResponseEnvelope,
    responses={
        405: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {"Wallet with address <address> does not exist."}
                    }
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Wallet with address <address> does not belong to the correct owner."
                        }
                    }
                }
            }
        },
        419: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": f"Wallet with address <address> does not have enough balance."
                        }
                    }
                }
            }
        },
        420: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": f"You are trying to make transaction from wallet with address <from_address> "
                            f"to same wallet with address <to_address>."
                        }
                    }
                }
            }
        },
    },
)
def make_transaction(
    request: MakeTransactionRequest,
    wallets: WalletRepositoryDependable,
) -> JSONResponse | dict[str, TransactionItemResponse]:
    try:
        from_wallet = wallets.get_wallet(request.private_key, request.from_key)
    except InvalidOwnerError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "message": f"Wallet with address <{request.from_key}> does not belong to the correct owner."
                }
            },
        )
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {
                    "message": f"Wallet with address <{request.from_key}> does not exist."
                }
            },
        )

    try:
        to_wallet = wallets.get(request.to_key)
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {
                    "message": f"Wallet with address <{request.to_key}> does not exist."
                }
            },
        )

    amount = request.amount
    if from_wallet.get_private_key() != to_wallet.get_private_key():
        amount *= 1 - 0.015

    transaction = Transaction(
        private_key=request.private_key,
        from_key=request.from_key,
        to_key=request.to_key,
        amount=amount,
    )

    try:
        wallets.add_transaction(transaction)
        return {
            "transaction": TransactionItemResponse(
                to_key=transaction.get_to_key(),
                from_key=transaction.get_from_key(),
                amount=transaction.get_amount(),
            )
        }
    except SameWalletsError:
        return JSONResponse(
            status_code=420,
            content={
                "error": {
                    "message": f"You are trying to make transaction from wallet with address <{request.from_key}> "
                    f"to same wallet with address <{request.to_key}>."
                }
            },
        )
    except NotEnoughBalanceError:
        return JSONResponse(
            status_code=419,
            content={
                "error": {
                    "message": f"Wallet with address <{request.from_key}> does not have enough balance."
                }
            },
        )


@transaction_api.get(
    "/transactions",
    status_code=200,
    response_model=TransactionListResponseEnvelope,
    responses={
        405: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {"Wallet with address <address> does not exist."}
                    }
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Wallet with address <address> does not belong to the correct owner."
                        }
                    }
                }
            }
        },
    },
)
def get_transactions(
    wallet_id: UUID,
    wallets: WalletRepositoryDependable,
    API_key: UUID = Header(alias="API_key"),
) -> dict[str, list[TransactionItemResponse]] | JSONResponse:
    try:
        transactions = wallets.get_transactions(API_key, wallet_id)
        return {
            "transactions": [
                TransactionItemResponse(
                    to_key=transaction.get_to_key(),
                    from_key=transaction.get_from_key(),
                    amount=transaction.get_amount(),
                )
                for transaction in transactions
            ]
        }
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {
                    "message": f"Wallet with address <{wallet_id}> does not exist."
                }
            },
        )
    except InvalidOwnerError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "message": f"Wallet with address <{wallet_id}> does not belong to the correct owner."
                }
            },
        )
