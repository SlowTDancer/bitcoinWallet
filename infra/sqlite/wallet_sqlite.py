import sqlite3
from dataclasses import dataclass
from uuid import UUID

from constants import DB_PATH
from core.errors import (
    InvalidOwnerError,
    NotEnoughBalanceError,
    SameWalletsError,
    WalletDoesNotExistError,
)
from core.transaction import Transaction
from core.wallet import Wallet, WalletRepository
from infra.sqlite.transaction_sqlite import TransactionSqlite


@dataclass
class WalletSqlite(WalletRepository):
    db_path: str = DB_PATH

    def __post_init__(self) -> None:
        self.transactions = TransactionSqlite(self.db_path)

    def create(self, wallet: Wallet) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        public_key = wallet.get_public_key()
        private_key = wallet.get_private_key()
        balance = wallet.get_balance()
        transactions = wallet.get_transactions()

        cursor.execute(
            "INSERT INTO wallets (public_key, private_key, balance) "
            "VALUES (?, ?, ?);",
            (str(public_key), str(private_key), balance),
        )

        for transaction in transactions:
            cursor.execute(
                "INSERT INTO wallets_transactions (wallet_key, transaction_key) "
                "VALUES (?, ?);",
                (str(public_key), str(transaction.get_key())),
            )

        connection.commit()
        connection.close()

        for transaction in transactions:
            self.transactions.create(transaction)

    def get(self, wallet_key: UUID) -> Wallet:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT private_key, balance FROM wallets" " WHERE public_key = ?",
            (str(wallet_key),),
        )
        result = cursor.fetchone()

        if result is None:
            connection.close()
            raise WalletDoesNotExistError(wallet_key)

        private_key = UUID(result[0])
        balance = result[1]

        cursor.execute(
            "SELECT transaction_key FROM wallets_transactions" " WHERE wallet_key = ?",
            (str(wallet_key),),
        )
        result = cursor.fetchall()
        connection.close()

        transactions: dict[UUID, Transaction] = {}
        for row in result:
            transaction_key = UUID(row[0])
            transactions[transaction_key] = self.transactions.get(transaction_key)

        return Wallet(wallet_key, private_key, balance, transactions)

    def add_transaction(self, transaction: Transaction) -> None:
        from_user_id = transaction.get_private_key()
        from_wallet_id = transaction.get_from_key()
        to_wallet_id = transaction.get_to_key()
        if from_wallet_id == to_wallet_id:
            raise SameWalletsError(from_wallet_id)

        from_wallet = self.get_wallet(from_user_id, from_wallet_id)
        to_wallet = self.get(to_wallet_id)

        if from_wallet.get_balance() < transaction.get_amount():
            raise NotEnoughBalanceError(from_wallet_id)
        else:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            amount = transaction.get_amount()
            from_wallet_balance = from_wallet.get_balance()
            to_wallet_balance = to_wallet.get_balance()

            cursor.execute(
                "UPDATE wallets SET balance = ? WHERE public_key = ?",
                (from_wallet_balance - amount, str(from_wallet_id)),
            )
            cursor.execute(
                "UPDATE wallets SET balance = ? WHERE public_key = ?",
                (to_wallet_balance + amount, str(to_wallet_id)),
            )
            cursor.execute(
                "INSERT INTO wallets_transactions (wallet_key, transaction_key) "
                "VALUES (?, ?)",
                (str(from_wallet_id), str(transaction.get_key())),
            )
            cursor.execute(
                "INSERT INTO wallets_transactions (wallet_key, transaction_key) "
                "VALUES (?, ?)",
                (str(to_wallet_id), str(transaction.get_key())),
            )

            connection.commit()
            connection.close()

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
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM wallets")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM wallets")
            connection.commit()
        cursor.execute("SELECT COUNT(*) FROM wallets_transactions")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM wallets_transactions")
            connection.commit()
        connection.close()
        self.transactions.clear()
