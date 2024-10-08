# BitcoinWallet

## Intro

The aim of the project is to create an HTTP API for the "Bitcoin Wallet" application.

Worry not, we will not do any blockchain operations. Instead, we will use SQLite for persistence. However, (fingers crossed) at this point you have enough knowledge to create a solution that one can (relatively) easily extend to use Postgres/MySQL or even the real blockchain.

Concurrency is also out of scope. You do not have to solve the so-called "double spending" issue, but you are very much encouraged to think about how you would tackle it.

## API Spec

`POST /users`
  - Registers user
  - Returns API key that can authenticate all subsequent requests for this user

`POST /wallets`
  - Requires API key
  - Create BTC wallet 
  - Deposits 1 BTC (or 100000000 satoshis) automatically to the new wallet
  - User may register up to 3 wallets
  - Returns wallet address and balance in BTC and USD

`GET /wallets/{address}`
  - Requires API key
  - Returns wallet address and balance in BTC and USD

`POST /transactions`
  - Requires API key
  - Makes a transaction from one wallet to another
  - Transaction is free if the same user is the owner of both wallets
  - System takes a 1.5% (of the transferred amount) fee for transfers to the foreign wallets

`GET /transactions`
  - Requires API key
  - Returns list of transactions

`GET /wallets/{address}/transactions`
  - Requires API key
  - returns transactions related to the wallet

`GET /statistics`
  - Requires pre-set (hard coded) Admin API key
  - Returns the total number of transactions and platform profit

## Technical requirements
  
- Python 3.11
- [FastAPI](https://fastapi.tiangolo.com/) as a web framework
- [SQLite](https://docs.python.org/3/library/sqlite3.html) for persistence
- Use publicaly available API of your choice for BTC -> USD conversion
- Decide the structure of the requests and responses yourselves
- Use "X-API-KEY" HTTP header to pass and validate API key on server side
- Implement only API endpoints (UI is out of scope)
- Concurrancy is out of scope
