from dataclasses import dataclass, field
from uuid import UUID

from core.errors import (
    InvalidOwnerError,
    SameWalletsError,
    WalletDoesNotExistError,
)
from core.transaction import Transaction
from core.wallet import Wallet, WalletRepository


@dataclass
class WalletInMemory(WalletRepository):
    wallets: dict[UUID, Wallet] = field(default_factory=dict)

    def create(self, wallet: Wallet) -> None:
        self.wallets[wallet.get_public_key()] = wallet

    def get(self, wallet_key: UUID) -> Wallet:
        try:
            return self.wallets[wallet_key]
        except KeyError:
            raise WalletDoesNotExistError(wallet_key)

    def get_wallet(self, user_key: UUID, wallet_key: UUID) -> Wallet:
        try:
            wallet = self.wallets[wallet_key]
            if wallet.get_private_key() != user_key:
                raise InvalidOwnerError(user_key)
            else:
                return wallet
        except KeyError:
            raise WalletDoesNotExistError(wallet_key)

    def add_transaction(self, transaction: Transaction) -> None:
        from_user_id = transaction.get_private_key()
        from_wallet_id = transaction.get_from_key()
        to_wallet_id = transaction.get_to_key()
        if from_wallet_id == to_wallet_id:
            raise SameWalletsError(from_wallet_id)

        from_wallet = self.get_wallet(from_user_id, from_wallet_id)
        to_wallet = self.get(to_wallet_id)
        
        amount = transaction.get_amount()
        from_wallet.update_balance(-amount)
        to_wallet.update_balance(amount)
        from_wallet.add_transaction(transaction)
        to_wallet.add_transaction(transaction)

    def get_transactions(self, user_key: UUID, wallet_key: UUID) -> list[Transaction]:
        return self.get_wallet(user_key, wallet_key).get_transactions()
