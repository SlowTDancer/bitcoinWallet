from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.repositories import RepositoryABC


@dataclass
class User:
    private_key: UUID = field(default_factory=uuid4)
    mail: str = "default@mail.com"
    wallets: list[UUID] = field(default_factory=list)

    def get_private_key(self) -> UUID:
        pass

    def get_mail(self) -> str:
        pass

    def get_wallets(self) -> list[UUID]:
        pass

    def add_wallet(self, wallet_key: UUID) -> None:
        pass


class UserRepository(RepositoryABC[User]):
    @abstractmethod
    def create(self, user: User) -> None:
        pass

    @abstractmethod
    def get(self, user_key: UUID) -> User:
        pass

    @abstractmethod
    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        pass
