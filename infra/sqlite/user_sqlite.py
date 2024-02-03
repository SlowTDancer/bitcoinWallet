import sqlite3
import uuid
from dataclasses import dataclass
from uuid import UUID

from constants import DB_PATH
from core.errors import UserDoesNotExistError, UserAlreadyExistsError, WalletAlreadyExistsError
from core.user import UserRepository, User


@dataclass
class UserSqlite(UserRepository):
    db_path: str = DB_PATH

    def create(self, user: User) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT private_key FROM users WHERE email = ?", (user.get_email(),))
        result = cursor.fetchone()

        if result is not None:
            connection.close()
            raise UserAlreadyExistsError(user.get_email())
        email = user.get_email()
        private_key = str(user.get_private_key())

        cursor.execute(
            "INSERT INTO users (private_key, email) "
            "VALUES (?, ?);",
            (
                private_key,
                email,
            ),
        )
        connection.commit()
        connection.close()

    def get(self, private_key: UUID) -> User:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM users WHERE private_key = ?", (str(private_key),))
        result = cursor.fetchone()
        if result is None:
            connection.close()
            raise UserDoesNotExistError(private_key)
        email = str(result[0])
        cursor.execute("SELECT public_key FROM users_wallets WHERE private_key = ?", (str(private_key),))
        result = cursor.fetchall()
        connection.close()
        if result is None:
            User(email, private_key)
        return User(email, private_key, [uuid.UUID(row[0]) for row in result])

    def _get_by_email(self, email: str) -> User | None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT private_key FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        if result is None:
            connection.close()
            return None
        user_private_key = uuid.UUID(result[0])
        cursor.execute("SELECT public_key FROM users_wallets WHERE private_key = ?", (str(user_private_key),))
        result = cursor.fetchall()
        connection.close()
        if result is None:
            return User(email, user_private_key)
        return User(email, user_private_key, [uuid.UUID(row[0]) for row in result])

    def add_wallet(self, user_key: UUID, wallet_key: UUID) -> None:
        user = self.get(user_key)
        result_list = [wallet_id for wallet_id in user.get_wallets()]
        if wallet_key in result_list:
            raise WalletAlreadyExistsError(wallet_key)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users_wallets (private_key, public_key) "
                       "VALUES (?, ?);",
                       (
                           str(user_key),
                           str(wallet_key),
                       ), )
        connection.commit()
        connection.close()

    def clear(self) -> None:
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM users")
            connection.commit()
        cursor.execute("SELECT COUNT(*) FROM users_wallets")
        count = cursor.fetchone()[0]
        if count != 0:
            cursor.execute("DELETE FROM users_wallets")
            connection.commit()
        connection.close()
