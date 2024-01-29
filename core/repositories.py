from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class RepositoryABC(Generic[T], ABC):
    @abstractmethod
    def create(self, item: T) -> None:
        pass

    @abstractmethod
    def get(self, item_key: UUID) -> T:
        pass
