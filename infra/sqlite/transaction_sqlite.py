from dataclasses import dataclass
from uuid import UUID

from core.errors import TransactionDoesNotExistError
from core.transaction import Transaction, TransactionRepository
from infra.sqlite.database_sqlite import SqliteDatabase


@dataclass
class TransactionSqlite(TransactionRepository):
    sqlite_database: SqliteDatabase

    def create(self, transaction: Transaction) -> None:
        key = str(transaction.get_key())
        to_key = str(transaction.get_to_key())
        private_key = str(transaction.get_private_key())
        from_key = str(transaction.get_from_key())
        amount = transaction.get_amount()

        query = (
            "INSERT INTO transactions (key, to_key, private_key, from_key, amount) "
            "VALUES (?, ?, ?, ?, ?);"
        )
        params = (
            key,
            to_key,
            private_key,
            from_key,
            amount,
        )
        self.sqlite_database.execute(query, params)

    def get(self, transaction_key: UUID) -> Transaction:
        query = (
            "SELECT to_key, private_key, from_key, amount"
            " FROM transactions WHERE key = ?"
        )
        params = (str(transaction_key),)
        result = self.sqlite_database.fetch_one(query, params)

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
        table_names = ("transactions",)
        self.sqlite_database.clear(table_names)
