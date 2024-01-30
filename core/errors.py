class UserDoesNotExistError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class WalletAlreadyExistsError(Exception):
    pass


class ConversionError(Exception):
    pass
