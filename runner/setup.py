import os

from fastapi import FastAPI

from infra.in_memory.transaction_in_memory import TransactionInMemory
from infra.in_memory.user_in_memory import UserInMemory
from infra.in_memory.wallet_in_memory import WalletInMemory


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router()

    # comment line below when you are using test-mode
    # os.environ["REPOSITORY_KIND"] = "sqlite"

    if os.getenv("REPOSITORY_KIND", "memory") == "sqlite":
        app.state.transactions = TransactionInDatabase()
        app.state.wallets = WalletInDatabase()
        app.state.users = UserInDatabase()
    else:
        app.state.transactions = TransactionInMemory()
        app.state.wallets = WalletInMemory()
        app.state.users = UserInMemory()

    return app
