import logging
from typing import Any, Optional

import requests.exceptions
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.validators import OrderParams

logger = logging.getLogger("trading_bot.orders")


class OrderError(Exception):
    pass


def _safe_avg_price(response: dict[str, Any]) -> str:
    avg = response.get("avgPrice", "0")
    if avg and avg != "0":
        try:
            if float(avg) > 0:
                return avg
        except (ValueError, TypeError):
            pass

    cum_quote = float(response.get("cumQuote", 0) or 0)
    exec_qty = float(response.get("executedQty", 0) or 0)
    if exec_qty > 0:
        computed = cum_quote / exec_qty
        return f"{computed:.8f} (computed)"

    order_price = response.get("price", "")
    if order_price:
        try:
            if float(order_price) > 0:
                return f"{order_price} (order price)"
        except (ValueError, TypeError):
            pass

    return "N/A"


def place_order(client: Client, params: OrderParams) -> dict[str, Any]:
    order_kwargs: dict[str, Any] = {
        "symbol": params.symbol,
        "side": params.side,
        "type": params.order_type,
        "quantity": params.quantity,
        "newOrderRespType": "RESULT",
    }

    if params.order_type == "LIMIT":
        order_kwargs["price"] = params.price
        order_kwargs["timeInForce"] = "GTC"

    logger.info(
        "Placing %s %s order | symbol=%s | qty=%s | price=%s",
        params.side,
        params.order_type,
        params.symbol,
        params.quantity,
        params.price if params.price else "MARKET",
    )
    logger.debug("Full order request: %s", order_kwargs)

    try:
        response: dict[str, Any] = client.futures_create_order(**order_kwargs)

        logger.info(
            "Order placed successfully | orderId=%s | status=%s | executedQty=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
        )
        logger.debug("Full order response: %s", response)
        return response

    except BinanceAPIException as exc:
        logger.error(
            "Binance API error | code=%s | msg=%s", exc.code, exc.message
        )
        raise OrderError(
            f"Binance API error (code {exc.code}): {exc.message}"
        ) from exc

    except BinanceRequestException as exc:
        logger.error("Binance request error: %s", exc)
        raise OrderError(f"Binance request error: {exc}") from exc

    except requests.exceptions.ConnectionError as exc:
        logger.error("Network connection error: %s", exc)
        raise OrderError(
            "Network error: Could not reach Binance. "
            "Check your internet connection."
        ) from exc

    except requests.exceptions.Timeout as exc:
        logger.error("Request timed out: %s", exc)
        raise OrderError(
            "Request timed out while contacting Binance API."
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error placing order: %s", exc)
        raise OrderError(f"Unexpected error: {exc}") from exc


def print_order_summary(params: OrderParams) -> None:
    print("\n" + "=" * 55)
    print("  ORDER REQUEST SUMMARY")
    print("=" * 55)
    print(f"  Symbol     : {params.symbol}")
    print(f"  Side       : {params.side}")
    print(f"  Order Type : {params.order_type}")
    print(f"  Quantity   : {params.quantity}")
    if params.order_type == "LIMIT" and params.price:
        print(f"  Price      : {params.price}")
    else:
        print(f"  Price      : MARKET (best available)")
    print("=" * 55)


def print_order_response(response: dict[str, Any]) -> None:
    avg_price = _safe_avg_price(response)
    print("\n" + "=" * 55)
    print("  ORDER RESPONSE")
    print("=" * 55)
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Client OID   : {response.get('clientOrderId', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Orig Qty     : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price    : {avg_price}")
    print(f"  Time in Force: {response.get('timeInForce', 'N/A')}")
    print("=" * 55 + "\n")
