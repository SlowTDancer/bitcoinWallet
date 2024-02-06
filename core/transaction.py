from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.repositories import RepositoryABC


@dataclass
class Transaction:
    key: UUID = field(default_factory=uuid4)
    to_key: UUID = field(default_factory=uuid4)
    private_key: UUID = field(default_factory=uuid4)
    from_key: UUID = field(default_factory=uuid4)
    amount: int = 1

    def get_key(self) -> UUID:
        return self.key

    def get_to_key(self) -> UUID:
        return self.to_key

    def get_private_key(self) -> UUID:
        return self.private_key

    def get_from_key(self) -> UUID:
        return self.from_key

    def get_amount(self) -> int:
        return self.amount


class TransactionRepository(RepositoryABC[Transaction]):
    @abstractmethod
    def create(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def get(self, transaction_key: UUID) -> Transaction:
        pass
