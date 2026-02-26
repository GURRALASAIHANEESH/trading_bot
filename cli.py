#!/usr/bin/env python3
"""
Binance Futures Demo Trading Bot - CLI Entry Point

Usage:
  python cli.py --symbol BTCUSDT --side BUY --order_type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --order_type LIMIT --quantity 0.001 --price 80000
"""

import argparse
import logging
import sys
from typing import Optional

from bot.logging_config import setup_logging
from bot.validators import validate_order_params, ValidationError
from bot.client import get_futures_client, BinanceClientError
from bot.orders import (
    place_order,
    print_order_summary,
    print_order_response,
    OrderError,
)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance USDT-M Futures Demo Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY "
            "--order_type MARKET --quantity 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL "
            "--order_type LIMIT --quantity 0.001 --price 80000\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT).",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL"],
        metavar="BUY|SELL",
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--order_type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT"],
        metavar="MARKET|LIMIT",
        help="Order type: MARKET or LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity as a positive float (e.g., 0.001).",
    )
    parser.add_argument(
        "--price",
        type=float,
        required=False,
        default=None,
        help="Limit price, required only for LIMIT orders.",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    setup_logging()
    log = logging.getLogger("trading_bot.cli")

    # Step 1: Parse arguments
    args = parse_args(argv)

    # Step 2: Validate
    try:
        params = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        log.error("Validation error: %s", exc)
        print(f"\n[ERROR] {exc}\n", file=sys.stderr)
        return 1

    # Step 3: Print summary
    print_order_summary(params)

    # Step 4: Build client
    try:
        client = get_futures_client()
    except BinanceClientError as exc:
        log.error("Client error: %s", exc)
        print(f"\n[ERROR] Configuration error: {exc}\n", file=sys.stderr)
        return 2

    # Step 5: Place order
    try:
        response = place_order(client, params)
    except OrderError as exc:
        log.error("Order failed: %s", exc)
        print(f"\n[ERROR] Order failed: {exc}\n", file=sys.stderr)
        return 3

    # Step 6: Print response
    print_order_response(response)
    print(f"[SUCCESS] Order placed. Order ID: {response.get('orderId')}\n")
    log.info(
        "Session complete. orderId=%s status=%s",
        response.get("orderId"),
        response.get("status"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
