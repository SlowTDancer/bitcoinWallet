from uuid import UUID, uuid4

import pytest

from core.errors import UserDoesNotExistError, UserAlreadyExistsError, WalletAlreadyExistsError, WalletLimitReachedError
from core.user import User
from infra.in_memory.user_in_memory import UserInMemory


def test_user_create() -> None:
    email = "default@gmail.com"
    user = User(email)

    assert isinstance(user.get_private_key(), UUID)
    assert isinstance(user.get_email(), str)
    assert isinstance(user.get_wallets(), list)


def test_user_get() -> None:
    email = "default@gmail.com"
    private_key = uuid4()
    user = User(email, private_key)

    assert user.get_email() == email
    assert user.get_private_key() == private_key
    assert user.get_wallets() == []


def test_user_add_wallet() -> None:
    email = "default@gmail.com"
    user = User(email)
    public_key = uuid4()

    assert len(user.get_wallets()) == 0

    user.add_wallet(public_key)

    assert len(user.get_wallets()) == 1
    assert user.get_wallets()[0] == public_key


def test_user_add_no_more_than_three_wallets() -> None:
    email = "default@gmail.com"
    user = User(email)
    public_key1 = uuid4()
    public_key2 = uuid4()
    public_key3 = uuid4()
    public_key4 = uuid4()

    user.add_wallet(public_key1)
    assert len(user.get_wallets()) == 1

    user.add_wallet(public_key2)
    assert len(user.get_wallets()) == 2

    user.add_wallet(public_key3)
    assert len(user.get_wallets()) == 3

    with pytest.raises(WalletLimitReachedError, match=str(email)):
        user.add_wallet(public_key4)
    assert len(user.get_wallets()) == 3


def test_user_in_memory_create_and_get() -> None:
    repo = UserInMemory()
    none_existent_user_id = uuid4()
    with pytest.raises(UserDoesNotExistError, match=str(none_existent_user_id)):
        repo.get(none_existent_user_id)

    email = "default@gmail.com"
    user = User(email)
    repo.create(user)

    assert repo.get(user.get_private_key()) == user

    with pytest.raises(UserAlreadyExistsError, match=str(email)):
        repo.create(user)


def test_user_in_memory_add_wallet() -> None:
    repo = UserInMemory()
    none_existent_user_id = uuid4()
    with pytest.raises(UserDoesNotExistError, match=str(none_existent_user_id)):
        repo.add_wallet(none_existent_user_id, uuid4())

    email = "default@gmail.com"
    user = User(email)
    repo.create(user)

    wallet_key = uuid4()
    repo.add_wallet(user.get_private_key(), wallet_key)

    with pytest.raises(WalletAlreadyExistsError, match=str(wallet_key)):
        repo.add_wallet(user.get_private_key(), wallet_key)
