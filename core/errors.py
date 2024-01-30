class TransactionDoesNotExistError(Exception):
    pass
  
  
class WalletDoesNotExistError(Exception):
    pass


class InvalidOwnerError(Exception):
    pass


class NotEnoughBalanceError(Exception):
    pass


class SameWalletsError(Exception):
    pass
