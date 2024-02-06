from uuid import UUID, uuid4

import pytest

from constants import TEST_DB_PATH
from core.errors import InvalidOwnerError, SameWalletsError, WalletDoesNotExistError
from core.transaction import Transaction
from core.wallet import Wallet, WalletRepository
from infra.in_memory.wallet_in_memory import WalletInMemory
from infra.sqlite.wallet_sqlite import WalletSqlite


def test_wallet_create() -> None:
    wallet = Wallet()

    assert isinstance(wallet.get_public_key(), UUID)
    assert isinstance(wallet.get_private_key(), UUID)
    assert isinstance(wallet.get_balance(), int)
    assert isinstance(wallet.get_transactions(), list)


def test_wallet_get() -> None:
    public_key = uuid4()
    private_key = uuid4()
    balance = 3

    wallet = Wallet(public_key, private_key, balance)

    assert wallet.get_public_key() == public_key
    assert wallet.get_private_key() == private_key
    assert wallet.get_balance() == balance
    assert wallet.get_transactions() == []


def test_wallet_update_balance() -> None:
    public_key = uuid4()
    private_key = uuid4()
    balance = 3

    wallet = Wallet(public_key, private_key, balance)
    add_amount = 4
    wallet.update_balance(add_amount)
    assert wallet.get_balance() == balance + add_amount


def test_wallet_add_transaction() -> None:
    public_key = uuid4()
    private_key = uuid4()
    balance = 3

    wallet = Wallet(public_key, private_key, balance)
    assert len(wallet.get_transactions()) == 0

    transaction = Transaction()

    wallet.add_transaction(transaction)

    assert len(wallet.get_transactions()) == 1
    assert wallet.get_transactions()[0] == transaction


def test_wallet_repo_create_and_get(repo: WalletRepository = WalletInMemory()) -> None:
    wallet = Wallet()

    repo.create(wallet)

    assert repo.get(wallet.get_public_key()) == wallet


def test_wallet_repo_should_not_get_unknown(
    repo: WalletRepository = WalletInMemory(),
) -> None:
    unknown_key = uuid4()

    with pytest.raises(WalletDoesNotExistError, match=str(unknown_key)):
        repo.get(unknown_key)


def test_wallet_repo_get_wallet(repo: WalletRepository = WalletInMemory()) -> None:
    user_key = uuid4()
    wallet = Wallet(private_key=user_key)

    repo.create(wallet)

    assert repo.get_wallet(user_key, wallet.get_public_key()) == wallet


def test_wallet_repo_should_not_get_wallet_of_diff_user(
    repo: WalletRepository = WalletInMemory(),
) -> None:
    user_key = uuid4()
    wallet = Wallet()

    repo.create(wallet)

    with pytest.raises(InvalidOwnerError, match=str(user_key)):
        repo.get_wallet(user_key, wallet.get_public_key())


def test_wallet_repo_should_not_get_unknown_wallet(
    repo: WalletRepository = WalletInMemory(),
) -> None:
    unknown_key = uuid4()
    user_key = uuid4()

    with pytest.raises(WalletDoesNotExistError, match=str(unknown_key)):
        repo.get_wallet(user_key, unknown_key)


def test_wallet_repo_should_not_transaction_to_same_wallet(
    repo: WalletRepository = WalletInMemory(),
) -> None:
    to_key = uuid4()
    from_key = to_key
    transaction = Transaction(to_key=to_key, from_key=from_key)

    with pytest.raises(SameWalletsError, match=str(to_key)):
        repo.add_transaction(transaction)


def test_wallet_repo_add_and_get_transaction(
    repo: WalletRepository = WalletInMemory(),
) -> None:
    wallet1 = Wallet(balance=5)
    wallet2 = Wallet()
    repo.create(wallet1)
    repo.create(wallet2)

    user_key = wallet1.get_private_key()
    fr = wallet1.get_public_key()
    fro = fr
    from_key = fro
    transaction = Transaction(
        private_key=user_key,
        to_key=wallet2.get_public_key(),
        from_key=from_key,
        amount=3,
    )

    repo.add_transaction(transaction)
    assert repo.get_transactions(user_key, from_key) == [transaction]


def test_wallet_sqlite_create_and_get() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_create_and_get(repo)
    repo.clear()


def test_wallet_sqlite_should_not_get_unknown() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_should_not_get_unknown(repo)
    repo.clear()


def test_wallet_sqlite_get_wallet() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_get_wallet(repo)
    repo.clear()


def test_wallet_sqlite_should_not_get_wallet_of_diff_user() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_should_not_get_wallet_of_diff_user(repo)
    repo.clear()


def test_wallet_sqlite_should_not_get_unknown_wallet() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_should_not_get_unknown_wallet(repo)
    repo.clear()


def test_wallet_sqlite_should_not_transaction_to_same_wallet() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_should_not_transaction_to_same_wallet(repo)
    repo.clear()


def test_wallet_sqlite_add_and_get_transaction() -> None:
    repo = WalletSqlite(TEST_DB_PATH)
    test_wallet_repo_add_and_get_transaction(repo)
    repo.clear()
