from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from constants import TRANSFER_FEE
from core.repositories import RepositoryABC
from core.wallet import Wallet


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

    def system_update(
        self, from_wallet: Wallet, to_wallet: Wallet, amount: float
    ) -> float:
        if from_wallet.get_private_key() != to_wallet.get_private_key():
            self.profit = TRANSFER_FEE * amount
            from_wallet.update_balance(-self.profit)
            return amount - self.profit
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
