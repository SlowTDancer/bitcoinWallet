class UserDoesNotExistError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class WalletAlreadyExistsError(Exception):
    pass


class WalletDoesNotExistError(Exception):
    pass


class WalletLimitReachedError(Exception):
    pass


class ConversionError(Exception):
    pass


class TransactionDoesNotExistError(Exception):
    pass


class InvalidOwnerError(Exception):
    pass


class NotEnoughBalanceError(Exception):
    pass


class SameWalletsError(Exception):
    pass


class TransactionStatisticDoesNotExistError(Exception):
    pass


class InvalidAdminAPIKeyError(Exception):
    pass
