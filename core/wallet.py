from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.repositories import RepositoryABC
from core.transaction import Transaction


@dataclass
class Wallet:
    public_key: UUID = field(default_factory=uuid4)
    private_key: UUID = field(default_factory=uuid4)
    balance: float = 1.0
    transactions: dict[UUID, Transaction] = field(default_factory=dict)

    def get_public_key(self) -> UUID:
        pass

    def get_private_key(self) -> UUID:
        pass

    def get_balance(self) -> float:
        pass

    def get_transactions(self) -> list[Transaction]:
        pass

    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass


class WalletRepository(RepositoryABC[Wallet]):
    @abstractmethod
    def create(self, wallet: Wallet) -> None:
        pass

    @abstractmethod
    def get(self, wallet_key: UUID) -> Wallet:
        pass

    @abstractmethod
    def add_transaction(self, wallet_key: UUID, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def get_wallet(self, user_key: UUID, wallet_key: UUID) -> Wallet:
        pass

    @abstractmethod
    def get_transactions(self, wallet_key: UUID) -> list[Transaction]:
        pass
