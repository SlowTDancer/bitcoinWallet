import os

from fastapi import FastAPI

from infra.fastapi.statistics import statistic_api
from infra.fastapi.transactions import transaction_api
from infra.fastapi.users import user_api
from infra.fastapi.wallets import wallet_api
from infra.in_memory.transaction_in_memory import TransactionInMemory
from infra.in_memory.transaction_statistic_in_memory import TransactionStatisticInMemory
from infra.in_memory.user_in_memory import UserInMemory
from infra.in_memory.wallet_in_memory import WalletInMemory
from infra.sqlite.transaction_sqlite import TransactionSqlite
from infra.sqlite.transaction_statistic_sqlite import TransactionStatisticSqlite
from infra.sqlite.user_sqlite import UserSqlite
from infra.sqlite.wallet_sqlite import WalletSqlite


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(user_api)
    app.include_router(wallet_api)
    app.include_router(transaction_api)
    app.include_router(statistic_api)

    # comment line below when you are using test-mode
    # os.environ["REPOSITORY_KIND"] = "sqlite"

    if os.getenv("REPOSITORY_KIND", "memory") == "sqlite":
        app.state.transactions = TransactionSqlite()
        app.state.wallets = WalletSqlite()
        app.state.users = UserSqlite()
        app.state.transaction_statistics = TransactionStatisticSqlite()
    else:
        app.state.transactions = TransactionInMemory()
        app.state.wallets = WalletInMemory()
        app.state.users = UserInMemory()
        app.state.transaction_statistics = TransactionStatisticInMemory()

    return app
