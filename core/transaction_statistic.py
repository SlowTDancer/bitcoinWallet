from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from constants import TRANSFER_FEE
from core.repositories import RepositoryABC


@dataclass
class TransactionStatistic:
    key: UUID = field(default_factory=uuid4)
    transaction_key: UUID = field(default_factory=uuid4)
    profit: float = 0.0

    def get_key(self) -> UUID:
        return self.key

    def get_transaction_key(self) -> UUID:
        return self.transaction_key

    def get_profit(self) -> float:
        return self.profit

    def calculate_profit(
        self, from_wallet_key: UUID, to_wallet_key: UUID, amount: float
    ) -> float:
        if from_wallet_key != to_wallet_key:
            self.profit = TRANSFER_FEE * amount
            return amount - self.get_profit()
        return amount


@dataclass
class Statistics:
    transactions_number: int = 0
    platform_profit: float = 0.0


class TransactionStatisticRepository(RepositoryABC[TransactionStatistic]):
    @abstractmethod
    def create(self, statistic: TransactionStatistic) -> None:
        pass

    @abstractmethod
    def get(self, key: UUID) -> TransactionStatistic:
        pass

    @abstractmethod
    def get_statistics(self) -> Statistics:
        pass
