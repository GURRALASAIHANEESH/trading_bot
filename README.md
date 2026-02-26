# Binance Futures Demo Trading Bot

A production-ready CLI trading bot that places **MARKET** and **LIMIT** orders
on the Binance USDT-M Futures Demo environment.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance client wrapper
│   ├── orders.py           # Order placement logic + console output
│   ├── validators.py       # Input validation
│   └── logging_config.py   # Logging setup (rotating file + console)
├── logs/
│   └── trading_bot.log     # Auto-created on first run
├── cli.py                  # CLI entry point (argparse)
├── .env.example            # Template for credentials
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- A Binance account with Futures enabled
- API Key + Secret from Binance with **Reading** and **Futures** permissions

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/GURRALASAIHANEESH/trading_bot.git
cd trading_bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

> Never commit your `.env` file. It is listed in `.gitignore`.

---

## How to Run

### MARKET order (BUY)

```bash
python cli.py --symbol BTCUSDT --side BUY --order_type MARKET --quantity 0.01
```

### LIMIT order (SELL)

```bash
python cli.py --symbol BTCUSDT --side SELL --order_type LIMIT --quantity 0.01 --price 80000
```

### Full help

```bash
python cli.py --help
```

---

## CLI Arguments

| Argument         | Required              | Description                            |
|------------------|-----------------------|----------------------------------------|
| `--symbol`       | Always                | Trading pair (e.g., `BTCUSDT`)         |
| `--side`         | Always                | `BUY` or `SELL`                        |
| `--order_type`   | Always                | `MARKET` or `LIMIT`                    |
| `--quantity`     | Always                | Positive float (e.g., `0.01`)          |
| `--price`        | LIMIT orders only     | Limit price (e.g., `80000`)            |

> Minimum notional value is 100 USDT. For BTCUSDT at ~$68,000,
> use quantity >= 0.01.

---

## Example Output

### MARKET BUY

```
=======================================================
  ORDER REQUEST SUMMARY
=======================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Order Type : MARKET
  Quantity   : 0.01
  Price      : MARKET (best available)
=======================================================

=======================================================
  ORDER RESPONSE
=======================================================
  Order ID     : 12548827267
  Client OID   : EgQ3jftPPkeIhHVmLRdVOF
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.010
  Executed Qty : 0.010
  Avg Price    : 68461.40000
  Time in Force: GTC
=======================================================

[SUCCESS] Order placed. Order ID: 12548827267
```

### LIMIT SELL

```
=======================================================
  ORDER REQUEST SUMMARY
=======================================================
  Symbol     : BTCUSDT
  Side       : SELL
  Order Type : LIMIT
  Quantity   : 0.01
  Price      : 80000.0
=======================================================

=======================================================
  ORDER RESPONSE
=======================================================
  Order ID     : 12548827465
  Client OID   : 6C2KWjdIZ74s50NYo9HKpJ
  Symbol       : BTCUSDT
  Side         : SELL
  Type         : LIMIT
  Status       : NEW
  Orig Qty     : 0.010
  Executed Qty : 0.000
  Avg Price    : 80000.00 (order price)
  Time in Force: GTC
=======================================================

[SUCCESS] Order placed. Order ID: 12548827465
```

---

## Logging

Logs are written to `logs/trading_bot.log` using a rotating file handler
(max 5 MB, 3 backups). Console only shows WARNING and above to stay non-noisy.

Log format:
```
2026-02-26 11:38:17 | INFO     | trading_bot.client | Initialising Binance Futures Demo client.
2026-02-26 11:38:17 | INFO     | trading_bot.client | Binance client initialised. Base URL: https://demo-fapi.binance.com
2026-02-26 11:38:17 | INFO     | trading_bot.orders | Placing BUY MARKET order | symbol=BTCUSDT | qty=0.01 | price=MARKET
2026-02-26 11:38:18 | INFO     | trading_bot.orders | Order placed successfully | orderId=12548827267 | status=FILLED | executedQty=0.010
2026-02-26 11:38:18 | INFO     | trading_bot.cli    | Session complete. orderId=12548827267 status=FILLED
```

---

## Error Handling

| Exit Code | Meaning                        |
|-----------|--------------------------------|
| `0`       | Success                        |
| `1`       | Input validation error         |
| `2`       | API key / client config error  |
| `3`       | Order placement / API error    |

---

## Assumptions

1. **Demo environment** — Uses `https://demo-fapi.binance.com` (the current
   official Binance Futures Demo endpoint, successor to `testnet.binancefuture.com`).
2. **One-way position mode** assumed (Binance default). Hedge Mode is not supported.
3. **`timeInForce=GTC`** (Good-Till-Cancelled) is used for all LIMIT orders.
4. **`newOrderRespType=RESULT`** is sent to receive full fill details immediately.
5. **Minimum notional** of 100 USDT applies on the demo environment.
   Use `quantity >= 0.01` for BTCUSDT.
6. `avgPrice` for an unfilled LIMIT order returns `"0"` from Binance.
   The bot falls back to order price or computes from `cumQuote / executedQty`.
7. Credentials are loaded from a `.env` file using `python-dotenv`.
   No credentials are hardcoded anywhere.

---
