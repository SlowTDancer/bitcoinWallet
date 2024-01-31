from abc import abstractmethod
from dataclasses import field, dataclass
from uuid import UUID

from core.errors import TransactionDoesNotExistError
from core.transaction import TransactionRepository, Transaction


@dataclass
class TransactionInMemory(TransactionRepository):
    transactions: dict[UUID, Transaction] = field(default_factory=dict)

    def create(self, transaction: Transaction) -> None:
        key = transaction.get_key()
        self.transactions[key] = transaction

    def get(self, transaction_key: UUID) -> Transaction:
        try:
            return self.transactions[transaction_key]
        except KeyError:
            raise TransactionDoesNotExistError(transaction_key)
