import uuid
from dataclasses import dataclass
from uuid import UUID

from core.errors import (
    UserAlreadyExistsError,
    UserDoesNotExistError,
    WalletAlreadyExistsError,
)
from core.user import User, UserRepository
from infra.sqlite.database_sqlite import SqliteDatabase


@dataclass
class UserSqlite(UserRepository):
    sqlite_database: SqliteDatabase

    def create(self, user: User) -> None:
        query = "SELECT private_key FROM users WHERE email = ?"
        params = (user.get_email(),)

        result = self.sqlite_database.fetch_one(query, params)

        if result is not None:
            raise UserAlreadyExistsError(user.get_email())
        email = user.get_email()
        private_key = str(user.get_private_key())

        query2 = "INSERT INTO users (private_key, email) " "VALUES (?, ?);"
        params2 = (
            private_key,
            email,
        )

        self.sqlite_database.execute(query2, params2)

    def get(self, private_key: UUID) -> User:
        query = "SELECT email FROM users WHERE private_key = ?"
        params = (str(private_key),)

        result = self.sqlite_database.fetch_one(query, params)

        if result is None:
            raise UserDoesNotExistError(private_key)

        email = str(result[0])
        user = self._get_by_email(email)
        if user is None:
            raise UserDoesNotExistError(private_key)
        return user

    def _get_by_email(self, email: str) -> User | None:
        query = "SELECT private_key FROM users WHERE email = ?"
        params = (email,)

        result = self.sqlite_database.fetch_one(query, params)

        if result is None:
            return None
        user_private_key = uuid.UUID(result[0])

        query2 = "SELECT public_key FROM users_wallets WHERE private_key = ?"
        params2 = (str(user_private_key),)

        result2 = self.sqlite_database.fetch_all(query2, params2)

        return (
            User(email, user_private_key)
            if result2 is None
            else User(email, user_private_key, [uuid.UUID(row[0]) for row in result2])
        )

    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        user = self.get(user_key)
        result_list = [wallet_id for wallet_id in user.get_wallets()]
        if wallet_key in result_list:
            raise WalletAlreadyExistsError(wallet_key)

        user.add_wallet(wallet_key)

        query = "INSERT INTO users_wallets (private_key, public_key) " "VALUES (?, ?);"
        params = (
            str(user_key),
            str(wallet_key),
        )

        self.sqlite_database.execute(query, params)

    def clear(self) -> None:
        table_names = (
            "users_wallets",
            "users",
        )
        self.sqlite_database.clear(table_names)
