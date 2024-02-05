from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from constants import MAX_WALLETS_PER_USER
from core.errors import WalletLimitReachedError
from core.repositories import RepositoryABC


@dataclass
class User:
    email: str
    private_key: UUID = field(default_factory=uuid4)
    wallets: list[UUID] = field(default_factory=list)

    def get_private_key(self) -> UUID:
        return self.private_key

    def get_email(self) -> str:
        return self.email

    def get_wallets(self) -> list[UUID]:
        return self.wallets

    def add_wallet(self, wallet_key: UUID) -> None:
        if len(self.get_wallets()) >= MAX_WALLETS_PER_USER:
            raise WalletLimitReachedError(self.get_email())

        self.wallets.append(wallet_key)


class UserRepository(RepositoryABC[User]):
    @abstractmethod
    def create(self, user: User) -> None:
        pass

    @abstractmethod
    def get(self, private_key: UUID) -> User:
        pass

    @abstractmethod
    def _get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        pass
