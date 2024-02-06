from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse

from constants import ERROR_RESPONSES
from core.errors import (
    InvalidOwnerError,
    NotEnoughBalanceError,
    SameWalletsError,
    UserDoesNotExistError,
    WalletDoesNotExistError,
)
from core.transaction import Transaction
from core.transaction_statistic import TransactionStatistic
from infra.fastapi.dependables import (
    TransactionStatisticRepositoryDependable,
    UserRepositoryDependable,
    WalletRepositoryDependable,
)
from infra.fastapi.wallets import (
    TransactionItemResponse,
    TransactionItemResponseEnvelope,
    TransactionListResponseEnvelope,
)

transaction_api = APIRouter(tags=["Transactions"])


class MakeTransactionRequest(BaseModel):
    from_key: UUID
    to_key: UUID
    amount: float


@transaction_api.post(
    "/transactions",
    status_code=201,
    response_model=TransactionItemResponseEnvelope,
    responses={
        404: ERROR_RESPONSES[404],
        405: ERROR_RESPONSES[405],
        409: ERROR_RESPONSES[409],
        413: ERROR_RESPONSES[413],
        419: ERROR_RESPONSES[419],
        420: ERROR_RESPONSES[420],
    },
)
def make_transaction(
    request: MakeTransactionRequest,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    transaction_statistics: TransactionStatisticRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> JSONResponse | dict[str, TransactionItemResponse]:
    try:
        users.get(api_key)
    except UserDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "User does not exist."}},
        )
    try:
        from_wallet = wallets.get_wallet(api_key, request.from_key)
    except InvalidOwnerError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "message": "Wallet with address "
                    f"<{request.from_key}> does "
                    "not belong to the correct owner."
                }
            },
        )
    except WalletDoesNotExistError:
        return JSONResponse(
            status_code=405,
            content={
                "error": {
                    "message": "Wallet with address "
                    f"<{request.from_key}> does not exist."
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

    if amount <= 0:
        return JSONResponse(
            status_code=413,
            content={
                "error": {"message": "Transaction amount must be a positive number."}
            },
        )

    transaction = Transaction(
        private_key=api_key,
        from_key=request.from_key,
        to_key=request.to_key,
        amount=amount,
    )

    try:
        transaction_statistic = TransactionStatistic(
            transaction_key=transaction.get_key()
        )
        transaction_statistic.system_update(wallets, from_wallet, to_wallet, amount)

        wallets.add_transaction(transaction)
        transaction_statistics.create(transaction_statistic)
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
                    "message": "You are trying to make transaction from "
                    f"wallet with address <{request.from_key}> "
                    f"to same wallet with address <{request.to_key}>."
                }
            },
        )
    except NotEnoughBalanceError:
        return JSONResponse(
            status_code=419,
            content={
                "error": {
                    "message": f"Wallet with address <{request.from_key}> does "
                    "not have enough balance."
                }
            },
        )


@transaction_api.get(
    "/transactions",
    status_code=200,
    response_model=TransactionListResponseEnvelope,
    responses={
        404: ERROR_RESPONSES[404],
    },
)
def get_transactions(
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, list[TransactionItemResponse]] | JSONResponse:
    try:
        user = users.get(api_key)
    except UserDoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "User does not exist."}},
        )

    wallet_ids = user.get_wallets()
    user_transactions = [
        wallets.get_transactions(api_key, wallet_id) for wallet_id in wallet_ids
    ]
    transactions = []
    for wallet_transactions in user_transactions:
        for transaction in wallet_transactions:
            if transaction not in transactions:
                transactions.append(transaction)
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
