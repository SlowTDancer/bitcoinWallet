from dataclasses import dataclass
from uuid import UUID

from core.errors import TransactionStatisticDoesNotExistError
from core.transaction_statistic import (
    Statistics,
    TransactionStatistic,
    TransactionStatisticRepository,
)
from infra.sqlite.database_sqlite import SqliteDatabase


@dataclass
class TransactionStatisticSqlite(TransactionStatisticRepository):
    sqlite_database: SqliteDatabase

    def create(self, statistic: TransactionStatistic) -> None:
        key = str(statistic.get_key())
        transaction_key = str(statistic.get_transaction_key())
        profit = statistic.get_profit()

        query = (
            "INSERT INTO transaction_statistics (key, transaction_key, profit) "
            "VALUES (?, ?, ?);"
        )
        params = (
            key,
            transaction_key,
            profit,
        )

        self.sqlite_database.execute(query, params)

    def get(self, key: UUID) -> TransactionStatistic:
        query = (
            "SELECT transaction_key, profit FROM transaction_statistics"
            " WHERE key = ?"
        )
        params = (str(key),)

        result = self.sqlite_database.fetch_one(query, params)

        if result is None:
            raise TransactionStatisticDoesNotExistError(key)
        return TransactionStatistic(
            key=key,
            transaction_key=UUID(result[0]),
            profit=result[1],
        )

    def get_statistics(self) -> Statistics:
        query = (
            "SELECT COUNT(transaction_key), ifnull(SUM(profit), 0) "
            "FROM transaction_statistics"
        )
        params = ()

        result = self.sqlite_database.fetch_one(query, params)
        return Statistics(int(result[0]), int(result[1]))

    def clear(self) -> None:
        table_names = ("transaction_statistics",)
        self.sqlite_database.clear(table_names)
