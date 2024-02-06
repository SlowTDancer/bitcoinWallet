from dataclasses import dataclass
from uuid import UUID

from core.errors import InvalidOwnerError, SameWalletsError, WalletDoesNotExistError
from core.transaction import Transaction
from core.wallet import Wallet, WalletRepository
from infra.sqlite.database_sqlite import SqliteDatabase
from infra.sqlite.transaction_sqlite import TransactionSqlite


@dataclass
class WalletSqlite(WalletRepository):
    sqlite_database: SqliteDatabase

    def __post_init__(self) -> None:
        self.transactions = TransactionSqlite(self.sqlite_database)

    def create(self, wallet: Wallet) -> None:
        public_key = wallet.get_public_key()
        private_key = wallet.get_private_key()
        balance = wallet.get_balance()
        transactions = wallet.get_transactions()

        query = (
            "INSERT INTO wallets (public_key, private_key, balance) "
            "VALUES (?, ?, ?);"
        )
        params = (
            str(public_key),
            str(private_key),
            balance,
        )
        self.sqlite_database.execute(query, params)

        for transaction in transactions:
            query2 = (
                "INSERT INTO wallets_transactions (wallet_key, transaction_key) "
                "VALUES (?, ?);"
            )
            params2 = (
                str(public_key),
                str(transaction.get_key()),
            )
            self.sqlite_database.execute(query2, params2)

        for transaction in transactions:
            self.transactions.create(transaction)

    def get(self, wallet_key: UUID) -> Wallet:
        query = "SELECT private_key, balance FROM wallets WHERE public_key = ?"
        params = (str(wallet_key),)

        result = self.sqlite_database.fetch_one(query, params)

        if result is None:
            raise WalletDoesNotExistError(wallet_key)

        private_key = UUID(result[0])
        balance = result[1]

        query2 = "SELECT transaction_key FROM wallets_transactions WHERE wallet_key = ?"
        params2 = (str(wallet_key),)

        result2 = self.sqlite_database.fetch_all(query2, params2)

        transactions: dict[UUID, Transaction] = {}
        for row in result2:
            transaction_key = UUID(row[0])
            transactions[transaction_key] = self.transactions.get(transaction_key)

        return Wallet(wallet_key, private_key, balance, transactions)

    def update_balance(self, wallet_key: UUID, amount: int) -> None:
        wallet = self.get(wallet_key)
        balance = wallet.get_balance()

        query = "UPDATE wallets SET balance = ? WHERE public_key = ?"
        params = (
            balance + amount,
            str(wallet_key),
        )

        self.sqlite_database.execute(query, params)

    def add_transaction(self, transaction: Transaction) -> None:
        from_user_id = transaction.get_private_key()
        from_wallet_id = transaction.get_from_key()
        to_wallet_id = transaction.get_to_key()

        if from_wallet_id == to_wallet_id:
            raise SameWalletsError(from_wallet_id)

        self.get_wallet(from_user_id, from_wallet_id)
        amount = transaction.get_amount()

        self.update_balance(from_wallet_id, -amount)
        self.update_balance(to_wallet_id, amount)

        query = (
            "INSERT INTO wallets_transactions (wallet_key, transaction_key) "
            "VALUES (?, ?)"
        )
        params = (
            str(from_wallet_id),
            str(transaction.get_key()),
        )
        params2 = (
            str(to_wallet_id),
            str(transaction.get_key()),
        )

        self.sqlite_database.execute(query, params)
        self.sqlite_database.execute(query, params2)

        self.transactions.create(transaction)

    def get_wallet(self, user_key: UUID, wallet_key: UUID) -> Wallet:
        wallet = self.get(wallet_key)
        if wallet.get_private_key() != user_key:
            raise InvalidOwnerError(user_key)
        else:
            return wallet

    def get_transactions(self, user_key: UUID, wallet_key: UUID) -> list[Transaction]:
        return self.get_wallet(user_key, wallet_key).get_transactions()

    def clear(self) -> None:
        table_names = (
            "wallets_transactions",
            "wallets",
        )
        self.sqlite_database.clear(table_names)
        self.transactions.clear()
