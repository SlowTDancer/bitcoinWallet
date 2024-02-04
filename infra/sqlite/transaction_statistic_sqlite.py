import sqlite3
from dataclasses import dataclass
from uuid import UUID

from constants import DB_PATH
from core.errors import TransactionStatisticDoesNotExistError
from core.transaction_statistic import (
    Statistics,
    TransactionStatistic,
    TransactionStatisticRepository,
)


@dataclass
class TransactionStatisticSqlite(TransactionStatisticRepository):
    db_path: str = DB_PATH

    def create(self, statistic: TransactionStatistic) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        key = str(statistic.get_key())
        transaction_key = str(statistic.get_transaction_key())
        profit = statistic.get_profit()
        cursor.execute(
            "INSERT INTO transaction_statistics (key, transaction_key, profit) "
            "VALUES (?, ?, ?);",
            (
                key,
                transaction_key,
                profit,
            ),
        )
        connection.commit()
        connection.close()

    def get(self, key: UUID) -> TransactionStatistic:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT transaction_key, profit FROM transaction_statistics"
            " WHERE key = ?",
            (str(key),),
        )
        result = cursor.fetchone()
        connection.close()

        if result is None:
            raise TransactionStatisticDoesNotExistError(key)
        return TransactionStatistic(
            key,
            UUID(result[0]),
            result[1],
        )

    def get_statistics(self) -> Statistics:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(transaction_key), SUM(profit) FROM transaction_statistics",
        )
        result = cursor.fetchone()
        connection.close()
        if result is None:
            return Statistics()
        return Statistics(int(result[0]), float(result[1]))

    def clear(self) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM transaction_statistics")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM transaction_statistics")
            connection.commit()
        connection.close()
