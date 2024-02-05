from typing import Any

MAX_WALLETS_PER_USER = 3
DB_PATH = "main_sqlite.db"
TEST_DB_PATH = "../test_sqlite.db"
ADMIN_API_KEY = "002aa904-5f6d-4fa0-8bc6-e79094d3b599"
TRANSFER_FEE = 0.015
CONVERTER_URL = "https://blockchain.info/ticker"
ERROR_RESPONSES: dict[int, Any] = {
    401: {
        "content": {
            "application/json": {
                "example": {"error": {"message": "Invalid admin API key <key>"}}
            }
        }
    },
    404: {
        "content": {
            "application/json": {
                "example": {"error": {"message": "User does not exist."}}
            }
        }
    },
    405: {
        "content": {
            "application/json": {
                "example": {"error": {"Wallet with address <address> does not exist."}}
            }
        }
    },
    409: {
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Wallet with address <address> does"
                        " not belong to the correct owner."
                    }
                }
            }
        }
    },
    410: {
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "User's with email <email> wallet "
                        "quantity limit is reached."
                    }
                }
            }
        }
    },
    415: {
        "content": {
            "application/json": {
                "example": {"error": {"message": "conversion of btc to usd failed."}}
            }
        }
    },
    419: {
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "Wallet with address <address> does not have"
                        " enough balance."
                    }
                }
            }
        }
    },
    420: {
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "message": "You are trying to make transaction "
                        "from wallet with address <from_address> "
                        "to same wallet with address <to_address>."
                    }
                }
            }
        }
    },
}
