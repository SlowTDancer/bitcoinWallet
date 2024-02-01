from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from uuid import UUID

from constants import MAX_WALLETS_PER_USER
from core.errors import (
    UserAlreadyExistsError,
    UserDoesNotExistError,
    WalletAlreadyExistsError,
    WalletLimitReachedError,
)
from core.repositories import RepositoryABC
from core.user import User


@dataclass
class UserInMemory(RepositoryABC[User]):
    users: dict[UUID, User] = field(default_factory=dict)

    @abstractmethod
    def create(self, user: User) -> None:
        if self._get_by_email(user.get_email()) is not None:
            raise UserAlreadyExistsError()

        self.users[user.get_private_key()] = user

    @abstractmethod
    def get(self, user_key: UUID) -> User:
        try:
            return self.users[user_key]
        except KeyError:
            raise UserDoesNotExistError()

    @abstractmethod
    def _get_by_email(self, email: str) -> User | None:
        users = list(
            filter(lambda user: user.get_email() == email, self.users.values())
        )

        return users[0] if len(users) == 1 else None

    @abstractmethod
    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        user = self.get(user_key)
        if wallet_key in user.get_wallets():
            raise WalletAlreadyExistsError(wallet_key)

        if len(user.get_wallets()) >= MAX_WALLETS_PER_USER:
            raise WalletLimitReachedError(user.get_email())

        user.add_wallet(wallet_key)
        self.users[user_key] = user
