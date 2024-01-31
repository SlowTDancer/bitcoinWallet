from dataclasses import dataclass, field
from uuid import UUID

from core.errors import (
    UserAlreadyExistsError,
    UserDoesNotExistError,
    WalletAlreadyExistsError,
)
from core.repositories import RepositoryABC
from core.user import User


@dataclass
class UserInMemory(RepositoryABC[User]):
    users: dict[UUID, User] = field(default_factory=dict)

    def create(self, user: User) -> None:
        if self._get_by_email(user.email) is not None:
            raise UserAlreadyExistsError(user.get_email())

        self.users[user.get_private_key()] = user

    def get(self, user_key: UUID) -> User:
        try:
            return self.users[user_key]
        except KeyError:
            raise UserDoesNotExistError(user_key)

    def _get_by_email(self, email: str) -> User | None:
        users = list(filter(lambda user: user.email == email, self.users.values()))

        if len(users) == 1:
            return users[0]

        return None

    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        user = self.get(user_key)
        if wallet_key in user.get_wallets():
            raise WalletAlreadyExistsError(wallet_key)

        user.add_wallet(wallet_key)
        self.users[user_key] = user
