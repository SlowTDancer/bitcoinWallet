import sqlite3
from dataclasses import dataclass
from uuid import UUID

from constants import DB_PATH
from core.errors import TransactionDoesNotExistError
from core.transaction import Transaction, TransactionRepository


@dataclass
class TransactionSqlite(TransactionRepository):
    db_path: str = DB_PATH

    def create(self, transaction: Transaction) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        key = str(transaction.get_key())
        to_key = str(transaction.get_to_key())
        private_key = str(transaction.get_private_key())
        from_key = str(transaction.get_from_key())
        amount = transaction.get_amount()

        cursor.execute(
            "INSERT INTO transactions (key, to_key, private_key, from_key, amount) "
            "VALUES (?, ?, ?, ?, ?);",
            (
                key,
                to_key,
                private_key,
                from_key,
                amount,
            ),
        )
        connection.commit()
        connection.close()

    def get(self, transaction_key: UUID) -> Transaction:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT to_key, private_key, from_key, amount FROM transactions"
            " WHERE key = ?",
            (str(transaction_key),),
        )
        result = cursor.fetchone()
        connection.close()

        if result is None:
            raise TransactionDoesNotExistError(transaction_key)
        return Transaction(
            transaction_key,
            UUID(result[0]),
            UUID(result[1]),
            UUID(result[2]),
            result[3],
        )

    def clear(self) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM transactions")
            connection.commit()
        connection.close()
