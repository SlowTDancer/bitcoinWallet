from abc import abstractmethod
from dataclasses import dataclass, field
from math import ceil
from uuid import UUID, uuid4

from constants import TRANSFER_FEE
from core.errors import NotEnoughBalanceError
from core.repositories import RepositoryABC
from core.wallet import Wallet, WalletRepository


@dataclass
class TransactionStatistic:
    key: UUID = field(default_factory=uuid4)
    transaction_key: UUID = field(default_factory=uuid4)
    profit: int = 0

    def get_key(self) -> UUID:
        return self.key

    def get_transaction_key(self) -> UUID:
        return self.transaction_key

    def get_profit(self) -> int:
        return self.profit

    def system_update(
        self,
        wallet_repo: WalletRepository,
        from_wallet: Wallet,
        to_wallet: Wallet,
        transaction_amount: int,
    ) -> None:
        if from_wallet.get_private_key() != to_wallet.get_private_key():
            self.profit = ceil(transaction_amount * TRANSFER_FEE)
        required_amount = transaction_amount + self.profit

        if from_wallet.get_balance() < required_amount:
            raise NotEnoughBalanceError(from_wallet.get_public_key())

        wallet_repo.update_balance(from_wallet.get_public_key(), -self.profit)


@dataclass
class Statistics:
    transactions_number: int = 0
    platform_profit: int = 0

    def get_transactions_number(self) -> int:
        return self.transactions_number

    def get_platform_profit(self) -> int:
        return self.platform_profit


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
