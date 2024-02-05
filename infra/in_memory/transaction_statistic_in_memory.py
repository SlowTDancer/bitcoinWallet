from dataclasses import dataclass, field
from uuid import UUID

from core.errors import TransactionStatisticDoesNotExistError
from core.transaction_statistic import (
    Statistics,
    TransactionStatistic,
    TransactionStatisticRepository,
)


@dataclass
class TransactionStatisticInMemory(TransactionStatisticRepository):
    transaction_statistics: dict[UUID, TransactionStatistic] = field(
        default_factory=dict
    )

    def create(self, statistic: TransactionStatistic) -> None:
        key = statistic.get_key()

        self.transaction_statistics[key] = statistic

    def get(self, key: UUID) -> TransactionStatistic:
        try:
            return self.transaction_statistics[key]
        except KeyError:
            raise TransactionStatisticDoesNotExistError(key)

    def get_statistics(self) -> Statistics:
        profit = 0.0
        for statistic in self.transaction_statistics.values():
            profit += statistic.get_profit()

        return Statistics(
            transactions_number=len(self.transaction_statistics.values()),
            platform_profit=profit,
        )