from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from constants import BITCOIN
from core.repositories import RepositoryABC
from core.transaction import Transaction


@dataclass
class Wallet:
    public_key: UUID = field(default_factory=uuid4)
    private_key: UUID = field(default_factory=uuid4)
    balance: int = BITCOIN
    transactions: dict[UUID, Transaction] = field(default_factory=dict)

    def get_public_key(self) -> UUID:
        return self.public_key

    def get_private_key(self) -> UUID:
        return self.private_key

    def get_balance(self) -> int:
        return self.balance

    def get_transactions(self) -> list[Transaction]:
        if len(self.transactions) == 0:
            return []
        return list(self.transactions.values())

    def update_balance(self, amount: int) -> None:
        self.balance += amount

    def add_transaction(self, transaction: Transaction) -> None:
        transaction_id = transaction.get_key()
        self.transactions[transaction_id] = transaction


class WalletRepository(RepositoryABC[Wallet]):
    @abstractmethod
    def create(self, wallet: Wallet) -> None:
        pass

    @abstractmethod
    def get(self, wallet_key: UUID) -> Wallet:
        pass

    @abstractmethod
    def update_balance(self, wallet_key: UUID, amount: int) -> None:
        pass

    @abstractmethod
    def add_transaction(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def get_wallet(self, user_key: UUID, wallet_key: UUID) -> Wallet:
        pass

    @abstractmethod
    def get_transactions(self, user_key: UUID, wallet_key: UUID) -> list[Transaction]:
        pass
