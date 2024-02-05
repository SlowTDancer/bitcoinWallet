from uuid import UUID, uuid4

from sympy.testing import pytest

from constants import TRANSFER_FEE, TEST_DB_PATH
from core.errors import NotEnoughBalanceError, TransactionStatisticDoesNotExistError
from core.transaction_statistic import (
    TransactionStatistic,
    TransactionStatisticRepository,
    Statistics,
)
from core.wallet import Wallet
from infra.in_memory.transaction_statistic_in_memory import TransactionStatisticInMemory
from infra.sqlite.transaction_statistic_sqlite import TransactionStatisticSqlite


def test_transaction_statistic_create() -> None:
    transaction_statistic = TransactionStatistic()

    assert isinstance(transaction_statistic.get_key(), UUID)
    assert isinstance(transaction_statistic.get_transaction_key(), UUID)
    assert isinstance(transaction_statistic.get_profit(), float)


def test_transaction_statistic_get() -> None:
    key = uuid4()
    transaction_key = uuid4()
    profit = 1.25

    transaction_statistic = TransactionStatistic(key, transaction_key, profit)
    assert transaction_statistic.get_key() == key
    assert transaction_statistic.get_transaction_key() == transaction_key
    assert transaction_statistic.get_profit() == profit


def test_transaction_statistic_system_update_same_user_wallets() -> None:
    transaction_statistic = TransactionStatistic()
    user_key = uuid4()
    balance = 150
    from_wallet = Wallet(private_key=user_key, balance=balance)
    to_wallet = Wallet(private_key=user_key, balance=0.0)
    amount = 100
    transaction_statistic.system_update(from_wallet, to_wallet, amount)
    assert transaction_statistic.get_profit() == 0.0
    assert from_wallet.get_balance() == balance


def test_transaction_statistic_system_update_different_user_wallets() -> None:
    transaction_statistic = TransactionStatistic()
    balance = 150
    from_wallet = Wallet(balance=balance)
    to_wallet = Wallet()
    amount = 100
    transaction_statistic.system_update(from_wallet, to_wallet, amount)
    profit = amount * TRANSFER_FEE
    assert from_wallet.get_balance() == (balance - profit)
    assert transaction_statistic.get_profit() == profit


def test_transaction_statistic_system_update_not_enough_balance() -> None:
    transaction_statistic = TransactionStatistic()
    balance = 10
    from_wallet = Wallet(balance=balance)
    to_wallet = Wallet()
    amount = 100
    with pytest.raises(NotEnoughBalanceError, match=str(from_wallet.get_public_key())):
        transaction_statistic.system_update(from_wallet, to_wallet, amount)


def test_statistics_create() -> None:
    statistic = Statistics()

    assert isinstance(statistic.get_platform_profit(), float)
    assert isinstance(statistic.get_transactions_number(), int)


def test_statistics_get() -> None:
    platform_profit = 2.5
    transactions_number = 2

    statistic = Statistics(transactions_number, platform_profit)

    assert statistic.get_transactions_number() == transactions_number
    assert statistic.get_platform_profit() == platform_profit


def test_transaction_statistic_repo_create_and_get(
    repo: TransactionStatisticRepository = TransactionStatisticInMemory(),
) -> None:
    transaction_statistic = TransactionStatistic()

    repo.create(transaction_statistic)

    assert repo.get(transaction_statistic.get_key()) == transaction_statistic


def test_transaction_statistic_repo_should_not_get_unknown(
    repo: TransactionStatisticRepository = TransactionStatisticInMemory(),
) -> None:
    unknown_key = uuid4()

    with pytest.raises(TransactionStatisticDoesNotExistError, match=str(unknown_key)):
        repo.get(unknown_key)


def test_transaction_statistic_repo_get_statistics_on_empty(
    repo: TransactionStatisticRepository = TransactionStatisticInMemory(),
) -> None:
    statistics = repo.get_statistics()

    assert statistics.get_transactions_number() == 0
    assert statistics.get_platform_profit() == 0.0


def test_transaction_statistic_repo_get_statistics(
    repo: TransactionStatisticRepository = TransactionStatisticInMemory(),
) -> None:
    profit = 1.25
    transaction_statistic = TransactionStatistic(profit=profit)

    repo.create(transaction_statistic)
    statistics = repo.get_statistics()

    assert statistics.get_transactions_number() == 1
    assert statistics.get_platform_profit() == profit


def test_transaction_statistic_sqlite_get_statistics_create_and_get() -> None:
    repo = TransactionStatisticSqlite(TEST_DB_PATH)
    test_transaction_statistic_repo_create_and_get(repo)
    repo.clear()


def test_transaction_statistic_sqlite_get_statistics_on_empty() -> None:
    repo = TransactionStatisticSqlite(TEST_DB_PATH)
    test_transaction_statistic_repo_get_statistics_on_empty(repo)
    repo.clear()


def test_transaction_statistic_sqlite_get_statistics() -> None:
    repo = TransactionStatisticSqlite(TEST_DB_PATH)
    test_transaction_statistic_repo_get_statistics(repo)
    repo.clear()


def test_transaction_statistic_sqlite_should_not_get_unknown() -> None:
    repo = TransactionStatisticSqlite(TEST_DB_PATH)
    test_transaction_statistic_repo_should_not_get_unknown(repo)
    repo.clear()

