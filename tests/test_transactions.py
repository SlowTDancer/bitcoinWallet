from uuid import UUID, uuid4

import pytest

from constants import TEST_DB_PATH
from core.errors import TransactionDoesNotExistError
from core.transaction import Transaction, TransactionRepository
from infra.in_memory.transaction_in_memory import TransactionInMemory
from infra.sqlite.transaction_sqlite import TransactionSqlite


def test_transaction_create() -> None:
    to_key = uuid4()
    from_key = uuid4()
    private_key = uuid4()
    amount = 2.6
    transaction = Transaction(
        from_key=from_key, to_key=to_key, amount=amount, private_key=private_key
    )
    assert isinstance(transaction.get_key(), UUID)
    assert isinstance(transaction.get_amount(), float)
    assert isinstance(transaction.get_private_key(), UUID)
    assert isinstance(transaction.get_to_key(), UUID)
    assert isinstance(transaction.get_from_key(), UUID)


def test_transaction_get() -> None:
    to_key = uuid4()
    from_key = uuid4()
    private_key = uuid4()
    amount = 3.1
    transaction = Transaction(
        from_key=from_key, to_key=to_key, amount=amount, private_key=private_key
    )
    assert transaction.get_private_key() == private_key
    assert transaction.get_amount() == amount
    assert transaction.get_from_key() == from_key
    assert transaction.get_to_key() == to_key
    assert transaction.get_private_key() != uuid4()

    new_amount = 5.6
    transaction.update_amount(new_amount)
    assert transaction.get_amount() != amount
    assert transaction.get_amount() == new_amount


def test_transaction_repository(
    repo: TransactionRepository = TransactionInMemory(),
) -> None:
    none_existent_transaction_id = uuid4()
    with pytest.raises(
        TransactionDoesNotExistError, match=str(none_existent_transaction_id)
    ):
        repo.get(none_existent_transaction_id)

    transaction1 = Transaction()
    transaction2 = Transaction()
    repo.create(transaction1)
    repo.create(transaction2)

    assert transaction1 == repo.get(transaction1.get_key())
    assert transaction2 == repo.get(transaction2.get_key())


def test_transaction_sqlite() -> None:
    repo = TransactionSqlite(TEST_DB_PATH)
    test_transaction_repository(repo)
    repo.clear()
