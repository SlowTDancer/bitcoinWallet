import sqlite3

connection = sqlite3.connect("../../test_sqlite.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS transactions;")
cursor.execute("DROP TABLE IF EXISTS wallets;")
cursor.execute("DROP TABLE IF EXISTS wallets_transactions;")
cursor.execute("DROP TABLE IF EXISTS users;")
cursor.execute("DROP TABLE IF EXISTS users_wallets;")
cursor.execute("DROP TABLE IF EXISTS transaction_statistics;")

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS transactions (
        [key] TEXT PRIMARY KEY,
        [to_key] TEXT,
        [private_key] TEXT,
        [from_key] TEXT,
        [amount] INT
    );
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS wallets (
        [public_key] TEXT PRIMARY KEY,
        [private_key] TEXT,
        [balance] INT
    );
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS wallets_transactions (
        [wallet_key] TEXT,
        [transaction_key] TEXT
    );
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        [private_key] TEXT PRIMARY KEY,
        [email] TEXT UNIQUE
    );
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users_wallets (
        [private_key] TEXT,
        [public_key] TEXT
    );
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS transaction_statistics (
        [key] TEXT PRIMARY KEY,
        [transaction_key] TEXT UNIQUE,
        [profit] INT
    );
"""
)

connection.commit()

connection.close()
